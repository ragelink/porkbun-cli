#!/usr/bin/env python3
"""
Domain services setup script for Porkbun CLI.

This script helps set up a domain with various service configurations like
Cloudflare, Google Workspace, or Microsoft Office 365.
"""

import os
import sys
import argparse
import subprocess
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import the customize_template module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from examples.customize_template import customize_template, TemplateError
except ImportError as e:
    logger.error(f"Failed to import customize_template module: {e}")
    sys.exit(1)

class SetupError(Exception):
    """Exception raised for errors in the domain setup process."""
    pass

def verify_domain_format(domain):
    """Verify domain name format."""
    if not isinstance(domain, str):
        raise ValueError("Domain must be a string")
    
    if '.' not in domain:
        raise ValueError(f"Invalid domain format: {domain} (missing TLD)")
    
    if domain.startswith('.') or domain.endswith('.'):
        raise ValueError(f"Invalid domain format: {domain} (starts or ends with dot)")
    
    return True

def setup_domain_with_service(domain, service, output_dir=None, dry_run=False, region=None):
    """Set up a domain with a specific service."""
    try:
        # Verify domain format
        verify_domain_format(domain)
        
        # Configure output directory
        if output_dir is None:
            output_dir = Path(f"configs_{domain}")
        else:
            output_dir = Path(output_dir)
        
        # Ensure output directory exists
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise SetupError(f"Permission denied when creating directory: {output_dir}")
        except OSError as e:
            raise SetupError(f"Failed to create directory {output_dir}: {e}")
        
        # Define template paths
        templates_dir = Path(__file__).parent / "templates"
        if not templates_dir.exists():
            raise SetupError(f"Templates directory not found: {templates_dir}")
            
        template_paths = {
            "cloudflare": templates_dir / "cloudflare_dns.json",
            "google": templates_dir / "google_workspace.json",
            "microsoft": templates_dir / "office365.json",
            "netlify": templates_dir / "netlify.json",
            "aws": templates_dir / "aws_route53.json",
            "github": templates_dir / "github_pages.json",
            "vercel": templates_dir / "vercel.json",
            "shopify": templates_dir / "shopify.json",
            "digitalocean": templates_dir / "digitalocean.json",
            "firebase": templates_dir / "firebase.json"
        }
        
        if service not in template_paths:
            available_services = ", ".join(template_paths.keys())
            logger.error(f"Unknown service: {service}")
            logger.info(f"Available services: {available_services}")
            return False
        
        template_file = template_paths[service]
        if not template_file.exists():
            raise FileNotFoundError(f"Template file not found: {template_file}")
        
        # Customize template
        output_file = output_dir / f"{domain}_{service}_dns.json"
        
        try:
            customized_template = customize_template(template_file, domain, output_file, region)
        except (FileNotFoundError, TemplateError, ValueError) as e:
            logger.error(f"Template customization failed: {e}")
            return False
        
        if dry_run:
            logger.info(f"[DRY RUN] Would apply {service} DNS configuration to {domain}")
            return True
        
        # Apply template using Porkbun CLI
        cmd = [
            "python", "-m", "porkbun.cli", "workflow", "setup-domain", 
            domain, "--dns-records", str(customized_template)
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Successfully applied {service} configuration to {domain}")
            if result.stdout:
                logger.debug(f"Command output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error applying {service} configuration: {e}")
            if e.stdout:
                logger.debug(f"Command stdout: {e.stdout}")
            if e.stderr:
                logger.error(f"Command stderr: {e.stderr}")
            return False
            
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return False
    except SetupError as e:
        logger.error(f"Setup error: {e}")
        return False
    except ValueError as e:
        logger.error(f"Value error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in setup_domain_with_service: {e}")
        return False

def main():
    """Main entry point."""
    try:
        parser = argparse.ArgumentParser(description="Set up domain with various service configurations")
        parser.add_argument("domain", help="Domain to configure")
        parser.add_argument("--service", 
                            choices=["cloudflare", "google", "microsoft", "netlify", "aws", 
                                     "github", "vercel", "shopify", "digitalocean", "firebase", "all"], 
                            required=True, help="Service to configure")
        parser.add_argument("--output-dir", help="Directory to save configuration files")
        parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
        parser.add_argument("--region", help="AWS region (only for AWS template)")
        parser.add_argument("--droplet-ip", help="Actual IP address of your DigitalOcean droplet")
        parser.add_argument("--firebase-app-id", help="Firebase app ID (if different from domain)")
        parser.add_argument("--shopify-subdomain", help="Shopify subdomain (if different from domain)")
        
        args = parser.parse_args()
        
        # Set logging level based on verbosity
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            
        # Validate domain
        try:
            verify_domain_format(args.domain)
        except ValueError as e:
            logger.error(f"Invalid domain: {e}")
            sys.exit(1)
            
        if args.service == "all":
            services = ["cloudflare", "google", "microsoft", "netlify", "aws", 
                        "github", "vercel", "shopify", "digitalocean", "firebase"]
            logger.info(f"Setting up domain {args.domain} with all services: {', '.join(services)}")
        else:
            services = [args.service]
            logger.info(f"Setting up domain {args.domain} with service: {args.service}")
        
        success_count = 0
        for service in services:
            result = setup_domain_with_service(args.domain, service, args.output_dir, args.dry_run, args.region)
            if result:
                success_count += 1
                
        total_services = len(services)
        if success_count == total_services:
            logger.info(f"All {total_services} services were set up successfully.")
        else:
            logger.warning(f"{success_count} of {total_services} services were set up successfully.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 