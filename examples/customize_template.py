#!/usr/bin/env python3
"""
Template customization script for Porkbun CLI service templates.

This script takes a template file and a domain name, and creates a customized
version of the template with domain-specific values.
"""

import json
import sys
import os
import logging
from pathlib import Path
from json.decoder import JSONDecodeError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TemplateError(Exception):
    """Exception raised for errors in the template customization process."""
    pass

def validate_template(template):
    """Validate template structure and content."""
    if not isinstance(template, list):
        raise TemplateError("Template must be a list of DNS records")
    
    if not template:
        raise TemplateError("Template cannot be empty")
    
    for i, record in enumerate(template):
        if not isinstance(record, dict):
            raise TemplateError(f"Record {i} must be a dictionary")
        
        # Check required fields
        required_fields = ['type', 'name', 'content']
        for field in required_fields:
            if field not in record:
                raise TemplateError(f"Record {i} is missing required field '{field}'")
        
        # Check valid record type
        valid_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'SRV', 'CAA']
        if record['type'] not in valid_types:
            raise TemplateError(f"Record {i} has invalid type '{record['type']}'")
            
        # Type-specific validations
        record_type = record['type']
        content = record['content']
        
        # A record validation (IPv4)
        if record_type == 'A':
            import re
            ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ipv4_pattern, content):
                raise TemplateError(f"Record {i}: Invalid IPv4 address in A record: {content}")
            # Check IP address values
            try:
                octets = [int(octet) for octet in content.split('.')]
                if any(octet < 0 or octet > 255 for octet in octets):
                    raise TemplateError(f"Record {i}: IPv4 address has octets outside valid range (0-255): {content}")
            except ValueError:
                raise TemplateError(f"Record {i}: Invalid IPv4 address format: {content}")
                
        # AAAA record validation (IPv6)
        elif record_type == 'AAAA':
            if ':' not in content:
                raise TemplateError(f"Record {i}: Invalid IPv6 address in AAAA record: {content}")
        
        # MX record validation
        elif record_type == 'MX':
            if 'priority' not in record:
                raise TemplateError(f"Record {i}: MX record missing required 'priority' field")
            try:
                priority = int(record['priority'])
                if priority < 0 or priority > 65535:
                    raise TemplateError(f"Record {i}: MX priority must be between 0 and 65535")
            except (ValueError, TypeError):
                raise TemplateError(f"Record {i}: MX priority must be an integer")
        
        # SRV record validation
        elif record_type == 'SRV':
            required_srv_fields = ['priority', 'weight', 'port']
            for field in required_srv_fields:
                if field not in record:
                    raise TemplateError(f"Record {i}: SRV record missing required field '{field}'")
            
            try:
                priority = int(record['priority'])
                weight = int(record['weight'])
                port = int(record['port'])
                
                if priority < 0 or priority > 65535:
                    raise TemplateError(f"Record {i}: SRV priority must be between 0 and 65535")
                if weight < 0 or weight > 65535:
                    raise TemplateError(f"Record {i}: SRV weight must be between 0 and 65535")
                if port < 0 or port > 65535:
                    raise TemplateError(f"Record {i}: SRV port must be between 0 and 65535")
            except (ValueError, TypeError):
                raise TemplateError(f"Record {i}: SRV priority, weight, and port must be integers")
        
        # Check TTL if present
        if 'ttl' in record:
            try:
                ttl = int(record['ttl'])
                if ttl < 60 or ttl > 86400:
                    logger.warning(f"Record {i}: TTL value {ttl} is outside recommended range (60-86400)")
            except (ValueError, TypeError):
                raise TemplateError(f"Record {i}: TTL must be an integer")
                
        # Check for potential placeholder values that should be replaced
        placeholder_patterns = ["DOMAIN", "EXAMPLE", "YOUR_", "REPLACE_"]
        for pattern in placeholder_patterns:
            if pattern in str(content).upper():
                logger.warning(f"Record {i}: Content may contain placeholder text: '{pattern}' in '{content}'")

def customize_template(template_file, domain, output_file=None, region=None):
    """Customize a template for a specific domain."""
    
    # Default output file name
    if output_file is None:
        template_path = Path(template_file)
        output_file = template_path.parent / f"{domain}_{template_path.name}"
    
    try:
        # Check if template file exists
        if not os.path.isfile(template_file):
            raise FileNotFoundError(f"Template file not found: {template_file}")
        
        # Load template
        try:
            with open(template_file, 'r') as f:
                template = json.load(f)
        except JSONDecodeError as e:
            raise TemplateError(f"Invalid JSON in template file: {e}")
        
        # Validate template
        validate_template(template)
        
        # Get domain parts
        if not isinstance(domain, str) or '.' not in domain:
            raise ValueError(f"Invalid domain name: {domain}")
        
        domain_parts = domain.split('.')
        domain_prefix = domain_parts[0]
        domain_hyphenated = domain.replace('.', '-')
        
        # Default AWS region if not provided
        aws_region = region if region else "us-east-1"
        
        # Customize records
        for record in template:
            # Office 365 MX record
            if record['type'] == 'MX' and 'protection.outlook.com' in record.get('content', ''):
                record['content'] = f"{domain_hyphenated}.mail.protection.outlook.com"
            
            # Netlify CNAME records
            if record['type'] == 'CNAME' and 'DOMAIN.netlify.app' in record.get('content', ''):
                record['content'] = record['content'].replace('DOMAIN', domain_hyphenated)
                
            # Netlify ACME challenge CNAME record
            if record['type'] == 'CNAME' and record['name'] == '_acme-challenge' and 'DOMAIN.acme.netlify.com' in record.get('content', ''):
                record['content'] = record['content'].replace('DOMAIN', domain)
            
            # AWS Route 53 records
            if 'amazonaws.com' in record.get('content', '') and 'DOMAIN' in record.get('content', ''):
                record['content'] = record['content'].replace('DOMAIN', domain)
                # Replace region placeholder
                if 'REGION' in record.get('content', ''):
                    record['content'] = record['content'].replace('REGION', aws_region)
                    
            # AWS CloudFront records
            if 'cloudfront.net' in record.get('content', '') and 'DOMAIN' in record.get('content', ''):
                record['content'] = record['content'].replace('DOMAIN', domain_hyphenated)
                
            # AWS SES and other region-specific records
            if 'REGION' in record.get('content', ''):
                record['content'] = record['content'].replace('REGION', aws_region)
                
            # GitHub Pages challenge record
            if record['type'] == 'TXT' and record['name'].startswith('_github-pages-challenge-'):
                record['name'] = record['name'].replace('USERNAME', domain_prefix)
                
            # GitHub Pages CNAME records
            if record['type'] == 'CNAME' and 'USERNAME.github.io' in record.get('content', ''):
                record['content'] = record['content'].replace('USERNAME', domain_prefix)
                
            # SPF records with domain placeholder
            if record['type'] == 'TXT' and 'v=spf1' in record.get('content', ''):
                record['content'] = record['content'].replace('_spfblog.DOMAIN', f"_spfblog.{domain}")
                record['content'] = record['content'].replace('DOMAIN', domain)
            
            # DMARC records
            if record['type'] == 'TXT' and record['name'] == '_dmarc':
                record['content'] = record['content'].replace('DOMAIN', domain.lower())
                record['content'] = record['content'].replace('EXAMPLE.COM', domain.upper())
                record['content'] = record['content'].replace('dmarc-reports@EXAMPLE.COM', f"dmarc@{domain}")
        
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write customized template
        try:
            with open(output_file, 'w') as f:
                json.dump(template, f, indent=2)
        except IOError as e:
            raise TemplateError(f"Failed to write output file: {e}")
        
        logger.info(f"Customized template saved to {output_file}")
        return output_file
    
    except Exception as e:
        logger.error(f"Error customizing template: {e}")
        raise

def main():
    """Main entry point."""
    try:
        if len(sys.argv) < 3:
            print("Usage: customize_template.py <template_file> <domain> [output_file] [region]")
            sys.exit(1)
        
        template_file = sys.argv[1]
        domain = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        region = sys.argv[4] if len(sys.argv) > 4 else None
        
        customize_template(template_file, domain, output_file, region)
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except TemplateError as e:
        logger.error(f"Template error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Value error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 