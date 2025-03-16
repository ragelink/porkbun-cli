# Commands Reference

This document provides a complete reference of all available commands in the Porkbun CLI.

## Account Management

### account ping
Check the API connection status.

```bash
porkbun account ping
```

### account info
Retrieve account information.

```bash
porkbun account info
```

### account pricing
Get pricing information for domains.

```bash
porkbun account pricing
```

## Configuration

### config add
Add a new profile with API credentials.

```bash
porkbun config add PROFILE_NAME --api-key YOUR_API_KEY --secret-key YOUR_SECRET_KEY [--make-default]
```

### config list
List all configured profiles.

```bash
porkbun config list
```

### config use
Switch to a different profile.

```bash
porkbun config use PROFILE_NAME
```

### config delete
Delete a profile.

```bash
porkbun config delete PROFILE_NAME
```

## Domain Management

### domains list-all
List all domains in your account.

```bash
porkbun domains list-all [--output table|json|csv]
```

### domains check
Check domain availability.

```bash
porkbun domains check DOMAIN [--tlds TLD1,TLD2,TLD3] [--suggest] [--compare]
```

### domains register
Register a new domain.

```bash
porkbun domains register DOMAIN [--years YEARS] [--whois-privacy ENABLED|DISABLED]
```

### domains renew
Renew a domain.

```bash
porkbun domains renew DOMAIN [--years YEARS]
```

### domains transfer
Transfer a domain to Porkbun.

```bash
porkbun domains transfer DOMAIN --auth-code AUTH_CODE [--years YEARS]
```

## DNS Management

### dns retrieve
List all DNS records for a domain.

```bash
porkbun dns retrieve DOMAIN [--output table|json|csv]
```

### dns create-record
Create a new DNS record.

```bash
porkbun dns create-record DOMAIN TYPE CONTENT TTL [--name NAME] [--priority PRIORITY]
```

Example:
```bash
porkbun dns create-record example.com A 192.168.1.1 600 --name www
```

### dns edit-record
Edit an existing DNS record.

```bash
porkbun dns edit-record DOMAIN RECORD_ID --content CONTENT [--ttl TTL] [--name NAME] [--priority PRIORITY]
```

### dns delete-record
Delete a DNS record.

```bash
porkbun dns delete-record DOMAIN RECORD_ID
```

### dns dnssec
Manage DNSSEC for a domain.

```bash
porkbun dns dnssec enable|disable|status DOMAIN
```

## SSL Certificates

### ssl retrieve
Get SSL certificate information.

```bash
porkbun ssl retrieve DOMAIN
```

### ssl create
Create a new SSL certificate.

```bash
porkbun ssl create DOMAIN
```

## URL Forwarding

### url list
List URL forwards for a domain.

```bash
porkbun url list DOMAIN
```

### url add
Add a URL forward.

```bash
porkbun url add DOMAIN FROM_PATH TO_URL [--type 301|302|cloaked]
```

### url delete
Delete a URL forward.

```bash
porkbun url delete DOMAIN FORWARD_ID
```

### url batch-add
Add multiple URL forwards from a JSON file.

```bash
porkbun url batch-add DOMAIN --file FORWARDS_FILE.json
```

## Email Forwarding

### email list
List email forwards for a domain.

```bash
porkbun email list DOMAIN
```

### email add
Add an email forward.

```bash
porkbun email add DOMAIN LOCAL_PART TO_EMAIL
```

Example:
```bash
porkbun email add example.com info info@another-domain.com
```

### email update
Update an email forward.

```bash
porkbun email update DOMAIN FORWARD_ID --to TO_EMAIL
```

### email delete
Delete an email forward.

```bash
porkbun email delete DOMAIN FORWARD_ID
```

## Workflows

### workflow list
List available workflows.

```bash
porkbun workflow list
```

### workflow setup-domain
Set up a domain with predefined services.

```bash
porkbun workflow setup-domain DOMAIN [--service SERVICE] [--template TEMPLATE_FILE]
```

Available services:
- cloudflare
- google
- office365
- netlify
- aws
- github
- vercel
- shopify
- digitalocean
- firebase
- all

## Batch Operations

### batch run
Run a batch file with multiple commands.

```bash
porkbun batch run BATCH_FILE.yaml [--dry-run]
```

## Domain Monitoring

### monitor list
List monitored domains.

```bash
porkbun monitor list
```

### monitor add
Add a domain to monitoring.

```bash
porkbun monitor add DOMAIN [--check-interval MINUTES] [--notification-email EMAIL]
```

### monitor remove
Remove a domain from monitoring.

```bash
porkbun monitor remove DOMAIN
```

## Formatting Options

Most commands support the following output formats:

- `--output table` (default): Format output as a table
- `--output json`: Format output as JSON
- `--output csv`: Format output as CSV

## Global Options

- `--profile PROFILE_NAME`: Use a specific profile for the command
- `--no-color`: Disable colored output
- `--verbose`: Enable verbose output
- `--version`: Show version information
- `--help`: Show help for a command 