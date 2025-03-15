# Porkbun CLI Quick Reference

A quick reference guide for the most commonly used Porkbun CLI commands.

## Setup & Configuration

```bash
# Setup configuration
python -m porkbun.cli config add default --api-key YOUR_API_KEY --secret-key YOUR_SECRET_KEY --make-default

# Test API connectivity
python -m porkbun.cli account ping
```

## Domain Management

```bash
# List all domains
python -m porkbun.cli domains list-all

# Check domain availability
python -m porkbun.cli domains check example.com

# Check with suggestions and price comparison
python -m porkbun.cli domains check example.com --suggest --compare

# Register a domain
python -m porkbun.cli domains register example.com --years 1 --whois-privacy --auto-renew

# Check WHOIS information
python -m porkbun.cli domains whois example.com
```

## DNS Management

```bash
# List DNS records
python -m porkbun.cli dns retrieve example.com

# Create A record
python -m porkbun.cli dns create-record example.com A 192.168.1.1 600

# Create CNAME record
python -m porkbun.cli dns create-record example.com CNAME example.org 600 --name www

# Create MX record
python -m porkbun.cli dns create-record example.com MX mail.example.com 600 --priority 10

# Create TXT record
python -m porkbun.cli dns create-record example.com TXT "v=spf1 include:_spf.example.com ~all" 600

# Delete record
python -m porkbun.cli dns delete-record example.com RECORD_ID
```

## SSL Management

```bash
# Retrieve SSL certificate
python -m porkbun.cli ssl retrieve example.com

# Generate new SSL certificate
python -m porkbun.cli ssl generate example.com
```

## Account Management

```bash
# Check account balance
python -m porkbun.cli account balance

# View recent transactions
python -m porkbun.cli account transactions --limit 5
```

## Portfolio Management

```bash
# Tag domains
python -m porkbun.cli account portfolio tag example.com --group clients --tags "important,client1"

# List domains by group
python -m porkbun.cli account portfolio list-domains --group clients
```

## Email Forwarding

```bash
# List email forwards
python -m porkbun.cli email retrieve-forwards example.com

# Create email forward
python -m porkbun.cli email create-forward example.com info@example.com destination@gmail.com
```

## Common Options

These options work with most commands:

```bash
# Use a specific profile
python -m porkbun.cli [command] --profile work

# Get verbose output
python -m porkbun.cli [command] --verbose

# Output as JSON
python -m porkbun.cli [command] --json
```

## Shorthand with Shell Alias

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias porkbun='python -m porkbun.cli'
```

Then use shortened commands:

```bash
porkbun domains list-all
porkbun dns retrieve example.com
```

## Common Workflows

### Setting up a new domain with basic DNS

```bash
# Register domain
python -m porkbun.cli domains register example.com --years 1 --whois-privacy --auto-renew

# Add DNS A record for root
python -m porkbun.cli dns create-record example.com A 192.168.1.1 600

# Add www subdomain
python -m porkbun.cli dns create-record example.com CNAME example.com 600 --name www

# Add MX records for email
python -m porkbun.cli dns create-record example.com MX mail.example.com 600 --priority 10

# Generate SSL certificate
python -m porkbun.cli ssl generate example.com
```

### Monitoring and maintenance

```bash
# Check expiring domains
python -m porkbun.cli monitor expiry --threshold 30

# Check account balance
python -m porkbun.cli account balance
``` 