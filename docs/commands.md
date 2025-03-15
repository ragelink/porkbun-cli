# Porkbun CLI Command Reference

This document provides a comprehensive reference for all available commands in the Porkbun CLI tool.

## Global Options

These options can be used with any command:

```
--help          Show help message and exit
--profile TEXT  Specify the profile to use (overrides default)
--verbose       Enable verbose output
--quiet         Suppress all output except errors
--json          Output in JSON format
```

## Configuration Commands

### config add

Add a new configuration profile.

```bash
python -m porkbun.cli config add PROFILE --api-key KEY --secret-key SECRET [--make-default]
```

**Options:**
- `--api-key TEXT`: Your Porkbun API key [required]
- `--secret-key TEXT`: Your Porkbun Secret API key [required]
- `--make-default`: Set this profile as the default

### config list

List all configured profiles.

```bash
python -m porkbun.cli config list
```

### config use

Switch to a different profile.

```bash
python -m porkbun.cli config use PROFILE
```

### config remove

Remove a configuration profile.

```bash
python -m porkbun.cli config remove PROFILE
```

## Account Commands

### account ping

Test API connectivity.

```bash
python -m porkbun.cli account ping
```

### account balance

Check account balance.

```bash
python -m porkbun.cli account balance
```

### account transactions

View transaction history.

```bash
python -m porkbun.cli account transactions [--limit INTEGER] [--before DATE] [--after DATE]
```

**Options:**
- `--limit INTEGER`: Maximum number of transactions to display
- `--before DATE`: Show transactions before this date (YYYY-MM-DD)
- `--after DATE`: Show transactions after this date (YYYY-MM-DD)

### account portfolio list-domains

List domains in your portfolio.

```bash
python -m porkbun.cli account portfolio list-domains [--group TEXT] [--tag TEXT]
```

**Options:**
- `--group TEXT`: Filter by domain group
- `--tag TEXT`: Filter by domain tag

### account portfolio tag

Tag a domain.

```bash
python -m porkbun.cli account portfolio tag DOMAIN [--group TEXT] [--tags TEXT]
```

**Options:**
- `--group TEXT`: Assign domain to a group
- `--tags TEXT`: Assign tags to domain (comma-separated)

### account portfolio groups

List all domain groups.

```bash
python -m porkbun.cli account portfolio groups
```

### account portfolio tags

List all domain tags.

```bash
python -m porkbun.cli account portfolio tags
```

## Domain Commands

### domains list-all

List all domains in your account.

```bash
python -m porkbun.cli domains list-all [--sort-by FIELD] [--filter TEXT]
```

**Options:**
- `--sort-by FIELD`: Sort by field (domain, expiry, status)
- `--filter TEXT`: Filter domains by text

### domains check

Check domain availability.

```bash
python -m porkbun.cli domains check DOMAIN [--suggest] [--compare] [--watch PRICE]
```

**Options:**
- `--suggest`: Show domain suggestions
- `--compare`: Compare prices across TLDs
- `--watch PRICE`: Add domain to price watch list

### domains register

Register a new domain.

```bash
python -m porkbun.cli domains register DOMAIN [--years INTEGER] [--whois-privacy] [--auto-renew]
```

**Options:**
- `--years INTEGER`: Registration period in years
- `--whois-privacy`: Enable WHOIS privacy
- `--auto-renew`: Enable auto-renewal

### domains bulk

Bulk register multiple domains.

```bash
python -m porkbun.cli domains bulk DOMAIN... [--years INTEGER] [--whois-privacy] [--auto-renew]
```

**Options:**
- Same as `domains register`

### domains watch-list

View domains in your price watch list.

```bash
python -m porkbun.cli domains watch-list
```

### domains whois

Check WHOIS information for a domain.

```bash
python -m porkbun.cli domains whois DOMAIN
```

## DNS Commands

### dns retrieve

Retrieve DNS records for a domain.

```bash
python -m porkbun.cli dns retrieve DOMAIN
```

### dns retrieve-records

Retrieve all DNS records for a domain.

```bash
python -m porkbun.cli dns retrieve-records DOMAIN
```

### dns create-record

Create a new DNS record.

```bash
python -m porkbun.cli dns create-record DOMAIN TYPE CONTENT TTL [--name NAME] [--priority PRIORITY]
```

**Arguments:**
- `DOMAIN`: Domain name
- `TYPE`: Record type (A, AAAA, CNAME, MX, TXT, etc.)
- `CONTENT`: Record content
- `TTL`: Time to live in seconds

**Options:**
- `--name NAME`: Subdomain name (@ for root)
- `--priority PRIORITY`: Priority (required for MX records)

### dns update-record

Update an existing DNS record.

```bash
python -m porkbun.cli dns update-record DOMAIN RECORD_ID [--type TYPE] [--content CONTENT] [--ttl TTL] [--name NAME] [--priority PRIORITY]
```

**Arguments:**
- `DOMAIN`: Domain name
- `RECORD_ID`: ID of the record to update

**Options:**
- Same as `dns create-record` but all optional

### dns delete-record

Delete a DNS record.

```bash
python -m porkbun.cli dns delete-record DOMAIN RECORD_ID
```

### dns batch-update

Create or update multiple DNS records at once using a JSON file.

```bash
python -m porkbun.cli dns batch-update DOMAIN BATCH_FILE
```

**Arguments:**
- `DOMAIN`: Domain name
- `BATCH_FILE`: Path to JSON file containing DNS records

The JSON file should contain an array of DNS record objects with the following fields:
- `type`: Record type (A, AAAA, MX, CNAME, TXT, etc.)
- `name`: Record name
- `content`: Record content
- `ttl`: Time to live (optional, defaults to 600)
- `id`: Record ID (only needed for updating existing records)

Example JSON file:
```json
[
    {"type": "A", "name": "test", "content": "192.0.2.1", "ttl": 600},
    {"type": "CNAME", "name": "www", "content": "example.com", "ttl": 600}
]
```

**Note on domain names**: When specifying record names, be aware that the Porkbun API may append the domain to the record name. For example, a record name of `www` might be displayed as `www.example.com.example.com` in the API response.

### dns batch-delete

Delete multiple DNS records at once.

```bash
python -m porkbun.cli dns batch-delete DOMAIN RECORD_IDS...
```

**Arguments:**
- `DOMAIN`: Domain name
- `RECORD_IDS`: One or more record IDs to delete

**Example:**
```bash
python -m porkbun.cli dns batch-delete example.com 12345 67890 54321
```

This will delete all the specified records and provide a summary of the operation.

### dns dnssec status

Check DNSSEC status.

```bash
python -m porkbun.cli dns dnssec status DOMAIN
```

### dns dnssec enable

Enable DNSSEC.

```bash
python -m porkbun.cli dns dnssec enable DOMAIN
```

### dns dnssec disable

Disable DNSSEC.

```bash
python -m porkbun.cli dns dnssec disable DOMAIN
```

## SSL Commands

### ssl retrieve

Retrieve SSL certificate for a domain.

```bash
python -m porkbun.cli ssl retrieve DOMAIN [--output-dir DIRECTORY]
```

**Options:**
- `--output-dir DIRECTORY`: Directory to save certificate files

### ssl generate

Generate a new SSL certificate.

```bash
python -m porkbun.cli ssl generate DOMAIN [--output-dir DIRECTORY]
```

**Options:**
- `--output-dir DIRECTORY`: Directory to save certificate files

## Email Commands

### email retrieve-forwards

Retrieve email forwards for a domain.

```bash
python -m porkbun.cli email retrieve-forwards DOMAIN
```

### email create-forward

Create a new email forward.

```bash
python -m porkbun.cli email create-forward DOMAIN EMAIL FORWARD_TO
```

**Arguments:**
- `DOMAIN`: Domain name
- `EMAIL`: Email address to forward from
- `FORWARD_TO`: Email address to forward to

### email delete-forward

Delete an email forward.

```bash
python -m porkbun.cli email delete-forward DOMAIN FORWARD_ID
```

## Automation Commands

### automation schedule

Schedule a command to run periodically.

```bash
python -m porkbun.cli automation schedule NAME COMMAND [--interval INTERVAL] [--at TIME]
```

**Arguments:**
- `NAME`: Unique name for the scheduled task
- `COMMAND`: Command to execute

**Options:**
- `--interval INTERVAL`: Interval (daily, weekly, monthly)
- `--at TIME`: Time to run (HH:MM)

### automation list

List scheduled tasks.

```bash
python -m porkbun.cli automation list
```

### automation remove

Remove a scheduled task.

```bash
python -m porkbun.cli automation remove NAME
```

## Monitor Commands

### monitor expiry

Monitor domain expiration.

```bash
python -m porkbun.cli monitor expiry [--threshold DAYS] [--notification-email EMAIL]
```

**Options:**
- `--threshold DAYS`: Alert when domains are this many days from expiring
- `--notification-email EMAIL`: Email to send notifications to

### monitor dns

Monitor DNS propagation.

```bash
python -m porkbun.cli monitor dns DOMAIN [--record-type TYPE] [--expected-value VALUE]
```

**Options:**
- `--record-type TYPE`: DNS record type to monitor
- `--expected-value VALUE`: Expected value for the record 

## URL Forwarding Commands

### url list-forwards

List URL forwards for a domain.

```bash
python -m porkbun.cli url list-forwards DOMAIN
```

**Arguments:**
- `DOMAIN`: Domain name

### url add-forward

Add URL forward for a domain.

```bash
python -m porkbun.cli url add-forward DOMAIN SOURCE DESTINATION [--type TYPE] [--title TITLE]
```

**Arguments:**
- `DOMAIN`: Domain name
- `SOURCE`: Source path (e.g., 'blog' or '/' for root)
- `DESTINATION`: Destination URL (e.g., 'https://example.com/blog')

**Options:**
- `--type TYPE`: Redirect type: 301 (permanent), 302 (temporary), or iframe. Default is 301.
- `--title TITLE`: Title for iframe redirects

### url delete-forward

Delete URL forward for a domain.

```bash
python -m porkbun.cli url delete-forward DOMAIN SOURCE
```

**Arguments:**
- `DOMAIN`: Domain name
- `SOURCE`: Source path to delete (e.g., 'blog' or '/' for root)

### url batch-add

Add multiple URL forwards for a domain using a JSON file.

```bash
python -m porkbun.cli url batch-add DOMAIN BATCH_FILE
```

**Arguments:**
- `DOMAIN`: Domain name
- `BATCH_FILE`: Path to JSON file containing URL forward definitions

The JSON file should contain an array of forwarding objects with the following fields:
- `source`: Source path (e.g., 'blog' or '/' for root)
- `destination`: Destination URL (e.g., 'https://example.com/blog')
- `type`: Redirect type ('301', '302', or 'iframe') - optional, defaults to '301'
- `title`: Title for iframe redirects - optional

Example JSON file:
```json
[
    {"source": "blog", "destination": "https://example.com/blog", "type": "301"},
    {"source": "shop", "destination": "https://shop.example.com", "type": "302"}
]
``` 