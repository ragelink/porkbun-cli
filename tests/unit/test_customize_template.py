"""
Unit tests for the customize_template.py script
"""

import json
import pytest
import os
import tempfile
from pathlib import Path
from examples.customize_template import customize_template


@pytest.fixture
def sample_office365_template():
    """Create a sample Office 365 template for testing"""
    template = [
        {
            "type": "MX",
            "name": "@",
            "content": "DOMAIN-com.mail.protection.outlook.com",
            "ttl": 3600,
            "priority": 0
        },
        {
            "type": "TXT",
            "name": "@",
            "content": "v=spf1 include:spf.protection.outlook.com -all",
            "ttl": 3600
        },
        {
            "type": "TXT",
            "name": "_dmarc",
            "content": "v=DMARC1; p=none; pct=100; rua=mailto:dmarc@DOMAIN; ruf=mailto:dmarc@DOMAIN; fo=1",
            "ttl": 3600
        }
    ]
    
    temp_dir = tempfile.gettempdir()
    template_path = os.path.join(temp_dir, 'test_template.json')
    
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    return template_path


def test_customize_template_mx_record(sample_office365_template):
    """Test customization of MX records"""
    domain = "example.com"
    output_file = os.path.join(tempfile.gettempdir(), f"{domain}_customized.json")
    
    # Run the customization
    result_path = customize_template(sample_office365_template, domain, output_file)
    
    # Verify the output file exists
    assert os.path.exists(output_file)
    assert result_path == output_file
    
    # Check contents
    with open(output_file, 'r') as f:
        result = json.load(f)
    
    # Check MX record was properly customized
    mx_record = next(r for r in result if r["type"] == "MX")
    assert mx_record["content"] == "example-com.mail.protection.outlook.com"
    
    # Clean up
    os.remove(output_file)


def test_customize_template_dmarc_record(sample_office365_template):
    """Test customization of DMARC records"""
    domain = "example.com"
    output_file = os.path.join(tempfile.gettempdir(), f"{domain}_customized.json")
    
    # Run the customization
    customize_template(sample_office365_template, domain, output_file)
    
    # Check contents
    with open(output_file, 'r') as f:
        result = json.load(f)
    
    # Check DMARC record was properly customized
    dmarc_record = next(r for r in result if r["name"] == "_dmarc")
    assert "dmarc@example.com" in dmarc_record["content"]
    assert "DOMAIN" not in dmarc_record["content"]
    
    # Clean up
    os.remove(output_file)


def test_customize_template_default_output(sample_office365_template):
    """Test customization with default output filename"""
    domain = "example.com"
    
    # Run the customization with default output
    result_path = customize_template(sample_office365_template, domain)
    
    # Verify the output file exists with default name
    assert os.path.exists(result_path)
    assert domain in os.path.basename(result_path)
    
    # Clean up
    os.remove(result_path)


def test_customize_template_nonexistent_file():
    """Test handling of nonexistent template file"""
    with pytest.raises(FileNotFoundError):
        customize_template("nonexistent_file.json", "example.com")


@pytest.fixture
def sample_netlify_template():
    """Create a sample Netlify template for testing"""
    template = [
        {
            "type": "CNAME",
            "name": "www",
            "content": "DOMAIN.netlify.app",
            "ttl": 3600
        },
        {
            "type": "CNAME",
            "name": "_acme-challenge",
            "content": "DOMAIN.acme.netlify.com",
            "ttl": 3600
        },
        {
            "type": "TXT",
            "name": "_dmarc",
            "content": "v=DMARC1; p=none; pct=100; rua=mailto:dmarc@DOMAIN; fo=1",
            "ttl": 3600
        }
    ]
    
    temp_dir = tempfile.gettempdir()
    template_path = os.path.join(temp_dir, 'test_netlify_template.json')
    
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    return template_path


def test_customize_netlify_cname_record(sample_netlify_template):
    """Test customization of Netlify CNAME records"""
    domain = "example.com"
    output_file = os.path.join(tempfile.gettempdir(), f"{domain}_customized_netlify.json")
    
    # Run the customization
    customize_template(sample_netlify_template, domain, output_file)
    
    # Check contents
    with open(output_file, 'r') as f:
        result = json.load(f)
    
    # Check CNAME record was properly customized
    cname_record = next(r for r in result if r["type"] == "CNAME" and r["name"] == "www")
    assert cname_record["content"] == "example-com.netlify.app"
    
    # Clean up
    os.remove(output_file)


def test_customize_netlify_acme_record(sample_netlify_template):
    """Test customization of Netlify ACME challenge CNAME record"""
    domain = "example.com"
    output_file = os.path.join(tempfile.gettempdir(), f"{domain}_customized_netlify_acme.json")
    
    # Run the customization
    customize_template(sample_netlify_template, domain, output_file)
    
    # Check contents
    with open(output_file, 'r') as f:
        result = json.load(f)
    
    # Check ACME challenge CNAME record was properly customized
    acme_record = next(r for r in result if r["name"] == "_acme-challenge")
    assert acme_record["content"] == "example.com.acme.netlify.com"
    
    # Clean up
    os.remove(output_file)


@pytest.fixture
def sample_aws_template():
    """Create a sample AWS Route 53 template for testing"""
    template = [
        {
            "type": "CNAME",
            "name": "www",
            "content": "DOMAIN.s3-website-REGION.amazonaws.com",
            "ttl": 300
        },
        {
            "type": "CNAME",
            "name": "cdn",
            "content": "DOMAIN.cloudfront.net",
            "ttl": 300
        },
        {
            "type": "TXT",
            "name": "@",
            "content": "v=spf1 include:amazonses.com include:_spfblog.DOMAIN ~all",
            "ttl": 300
        }
    ]
    
    temp_dir = tempfile.gettempdir()
    template_path = os.path.join(temp_dir, 'test_aws_template.json')
    
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    return template_path


@pytest.fixture
def sample_github_template():
    """Create a sample GitHub Pages template for testing"""
    template = [
        {
            "type": "CNAME",
            "name": "www",
            "content": "USERNAME.github.io",
            "ttl": 3600
        },
        {
            "type": "TXT",
            "name": "_github-pages-challenge-USERNAME",
            "content": "1234567890",
            "ttl": 3600
        }
    ]
    
    temp_dir = tempfile.gettempdir()
    template_path = os.path.join(temp_dir, 'test_github_template.json')
    
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    return template_path


def test_customize_aws_cname_record(sample_aws_template):
    """Test customization of AWS S3 website CNAME records"""
    domain = "example.com"
    output_file = os.path.join(tempfile.gettempdir(), f"{domain}_customized_aws.json")
    
    # Run the customization
    customize_template(sample_aws_template, domain, output_file)
    
    # Check contents
    with open(output_file, 'r') as f:
        result = json.load(f)
    
    # Check S3 CNAME record was properly customized
    s3_record = next(r for r in result if r["type"] == "CNAME" and r["name"] == "www")
    assert "example.com.s3-website-us-east-1.amazonaws.com" in s3_record["content"]
    
    # Check CloudFront record was properly customized
    cf_record = next(r for r in result if r["type"] == "CNAME" and r["name"] == "cdn")
    assert "example-com.cloudfront.net" in cf_record["content"]
    
    # Check SPF record
    spf_record = next(r for r in result if r["type"] == "TXT" and r["name"] == "@")
    assert "_spfblog.example.com" in spf_record["content"]
    
    # Clean up
    os.remove(output_file)


def test_customize_github_records(sample_github_template):
    """Test customization of GitHub Pages records"""
    domain = "example.com"
    output_file = os.path.join(tempfile.gettempdir(), f"{domain}_customized_github.json")
    
    # Run the customization
    customize_template(sample_github_template, domain, output_file)
    
    # Check contents
    with open(output_file, 'r') as f:
        result = json.load(f)
    
    # Check GitHub Pages CNAME record
    cname_record = next(r for r in result if r["type"] == "CNAME")
    assert cname_record["content"] == "example.github.io"
    
    # Check GitHub Challenge record
    challenge_record = next(r for r in result if r["type"] == "TXT")
    assert challenge_record["name"] == "_github-pages-challenge-example"
    
    # Clean up
    os.remove(output_file) 