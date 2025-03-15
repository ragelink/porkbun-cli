# Porkbun CLI Examples

This page contains practical examples of common use cases for the Porkbun CLI tool.

## Domain Management Examples

### Check Multiple Domains and Export Results

Check availability for multiple domains and export the results to a CSV file:

```bash
# Check multiple domains and save to CSV
python -m porkbun.cli domains check example.com example.org example.net --compare --csv domains.csv
```

### Register a Domain with Custom Settings

Register a domain with WHOIS privacy enabled, auto-renewal, and specific nameservers:

```bash
# Register with custom settings
python -m porkbun.cli domains register example.com --years 2 --whois-privacy --auto-renew --nameservers ns1.example.net ns2.example.net
```

### Bulk Domain Registration

Register multiple domains at once with the same settings:

```bash
# Bulk register domains
python -m porkbun.cli domains bulk example1.com example2.com example3.com --years 1 --whois-privacy
```

### Set Up Domain Price Alerts

Add domains to your price watch list to receive alerts when they drop below a certain price:

```bash
# Add to price watch
python -m porkbun.cli domains check premium-domain.com --watch 500.00
```

### Export List of Domains

Export a full list of your domains to a CSV file:

```bash
# Export domains to CSV
python -m porkbun.cli domains list-all --export domains.csv
```

### Find Domains Expiring Soon

List domains that are expiring within the next 60 days:

```bash
# Find expiring domains
python -m porkbun.cli domains list-all --expiring-within 60
```

## DNS Management Examples

### Set Up Common DNS Records for a New Domain

Set up standard DNS records for a new website:

```bash
# A record for root domain
python -m porkbun.cli dns create-record example.com A 192.168.1.1 600

# CNAME for www subdomain
python -m porkbun.cli dns create-record example.com CNAME example.com 600 --name www

# MX records for email
python -m porkbun.cli dns create-record example.com MX mail.example.com 600 --priority 10
python -m porkbun.cli dns create-record example.com MX mail2.example.com 600 --priority 20

# TXT record for SPF
python -m porkbun.cli dns create-record example.com TXT "v=spf1 include:_spf.example.com ~all" 600

# TXT record for DKIM
python -m porkbun.cli dns create-record example.com TXT "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb..." 600 --name dkim._domainkey
```

### Set Up Website Hosting with GitHub Pages

Configure DNS records for GitHub Pages hosting:

```bash
# Create A records for GitHub Pages IP addresses
python -m porkbun.cli dns create-record example.com A 185.199.108.153 600
python -m porkbun.cli dns create-record example.com A 185.199.109.153 600
python -m porkbun.cli dns create-record example.com A 185.199.110.153 600
python -m porkbun.cli dns create-record example.com A 185.199.111.153 600

# Create CNAME record for www subdomain
python -m porkbun.cli dns create-record example.com CNAME username.github.io 600 --name www
```

### Configure Google Workspace Email

Set up DNS records for Google Workspace (formerly G Suite):

```bash
# MX records for Gmail
python -m porkbun.cli dns create-record example.com MX aspmx.l.google.com 3600 --priority 1
python -m porkbun.cli dns create-record example.com MX alt1.aspmx.l.google.com 3600 --priority 5
python -m porkbun.cli dns create-record example.com MX alt2.aspmx.l.google.com 3600 --priority 5
python -m porkbun.cli dns create-record example.com MX alt3.aspmx.l.google.com 3600 --priority 10
python -m porkbun.cli dns create-record example.com MX alt4.aspmx.l.google.com 3600 --priority 10

# SPF record
python -m porkbun.cli dns create-record example.com TXT "v=spf1 include:_spf.google.com ~all" 3600

# DKIM record
python -m porkbun.cli dns create-record example.com TXT "v=DKIM1; k=rsa; p=YOUR_DKIM_KEY" 3600 --name google._domainkey

# DMARC record
python -m porkbun.cli dns create-record example.com TXT "v=DMARC1; p=reject; rua=mailto:dmarc@example.com" 3600 --name _dmarc
```

### Enable DNSSEC for a Domain

Enable DNSSEC for enhanced security:

```bash
# Enable DNSSEC
python -m porkbun.cli dns dnssec enable example.com

# Check DNSSEC status
python -m porkbun.cli dns dnssec status example.com
```

## SSL Certificate Examples

### Generate and Download SSL Certificate

Generate a new SSL certificate and download it to a specific directory:

```bash
# Generate new SSL certificate
python -m porkbun.cli ssl generate example.com --output-dir /path/to/certs
```

### Set Up SSL for Multiple Subdomains

Generate a wildcard certificate for all subdomains:

```bash
# Generate wildcard certificate
python -m porkbun.cli ssl generate example.com --wildcard
```

## Account Management Examples

### Check Account Balance Before Renewals

Check your account balance and ensure you have sufficient funds for upcoming renewals:

```bash
# Check account balance
python -m porkbun.cli account balance

# Find domains expiring soon
python -m porkbun.cli domains list-all --expiring-within 30
```

### Organize Domains with Tags and Groups

Organize your domains by client, project, or category:

```bash
# Tag domains for a client
python -m porkbun.cli account portfolio tag client1.com --group clients --tags "client1,active"
python -m porkbun.cli account portfolio tag client2.com --group clients --tags "client2,active"

# Tag personal domains
python -m porkbun.cli account portfolio tag personal.com --group personal --tags "blog,active"

# List domains by group
python -m porkbun.cli account portfolio list-domains --group clients
```

## Automation Examples

### Schedule Regular Tasks

Set up scheduled tasks for domain monitoring:

```bash
# Schedule daily expiration check
python -m porkbun.cli automation schedule check-expiry "python -m porkbun.cli domains list-all --expiring-within 30" --interval daily --at 08:00

# Schedule weekly balance check
python -m porkbun.cli automation schedule check-balance "python -m porkbun.cli account balance" --interval weekly --at 09:00
```

### Batch Operations with Shell Scripts

Create a shell script to perform multiple operations:

```bash
#!/bin/bash
# setup-domain.sh

# Activate virtual environment
source venv/bin/activate

# Set domain and IP address
DOMAIN=$1
IP_ADDRESS=$2

# Register domain
python -m porkbun.cli domains register $DOMAIN --years 1 --whois-privacy --auto-renew

# Set up DNS records
python -m porkbun.cli dns create-record $DOMAIN A $IP_ADDRESS 600
python -m porkbun.cli dns create-record $DOMAIN CNAME $DOMAIN 600 --name www
python -m porkbun.cli dns create-record $DOMAIN TXT "v=spf1 include:_spf.google.com ~all" 600

# Generate SSL certificate
python -m porkbun.cli ssl generate $DOMAIN --output-dir ./certs/$DOMAIN

echo "Domain $DOMAIN has been set up successfully!"
```

Usage:
```bash
./setup-domain.sh example.com 192.168.1.1
```

## Advanced Examples

### Use with jq for Advanced Filtering

Combine with jq for advanced filtering of JSON output:

```bash
# Find all domains with a specific TLD
python -m porkbun.cli domains list-all --json | jq '.domains[] | select(.tld == "com")'

# Count domains by TLD
python -m porkbun.cli domains list-all --json | jq 'group_by(.tld) | map({key: .[0].tld, count: length}) | from_entries'
```

### Export DNS Records for Backup

Backup all DNS records for a domain:

```bash
# Export all records to JSON file
python -m porkbun.cli dns retrieve-records example.com --json > example_com_dns_backup.json
```

### Bulk DNS Updates

Update multiple DNS records at once using a script:

```python
#!/usr/bin/env python
# bulk_dns_update.py

import json
import subprocess
import sys

def update_records(domain, old_ip, new_ip):
    # Get all DNS records
    result = subprocess.run(
        ["python", "-m", "porkbun.cli", "dns", "retrieve-records", domain, "--json"],
        capture_output=True, text=True
    )
    
    records = json.loads(result.stdout)
    
    # Filter for A records with the old IP
    for record in records.get("records", []):
        if record["type"] == "A" and record["content"] == old_ip:
            print(f"Updating record {record['id']} from {old_ip} to {new_ip}")
            
            # Update the record
            subprocess.run([
                "python", "-m", "porkbun.cli", "dns", "update-record",
                domain, record["id"], "--content", new_ip
            ])

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: ./bulk_dns_update.py DOMAIN OLD_IP NEW_IP")
        sys.exit(1)
    
    domain = sys.argv[1]
    old_ip = sys.argv[2]
    new_ip = sys.argv[3]
    
    update_records(domain, old_ip, new_ip)
```

Usage:
```bash
./bulk_dns_update.py example.com 192.168.1.1 192.168.1.2
``` 