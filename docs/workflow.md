# Workflow Commands

The workflow module provides commands for chaining multiple operations together, allowing you to automate common tasks and set up domains more efficiently.

## Setup Domain

The `setup-domain` command allows you to configure multiple aspects of a domain in a single operation, including DNS records, email forwards, and URL forwards.

```bash
python -m porkbun.cli workflow setup-domain DOMAIN [OPTIONS]
```

**Arguments:**
- `DOMAIN`: The domain to configure

**Options:**
- `--dns-records PATH`: Path to a JSON file containing DNS records
- `--email-forwards PATH`: Path to a JSON file containing email forwards
- `--url-forwards PATH`: Path to a JSON file containing URL forwards
- `--sequential/--parallel`: Run tasks sequentially or in parallel (default: sequential)

### Example

Set up a new domain with DNS records, email forwards, and URL forwards:

```bash
python -m porkbun.cli workflow setup-domain example.com \
    --dns-records dns.json \
    --email-forwards email_forwards.json \
    --url-forwards url_forwards.json
```

### Configuration Files

Each configuration file should follow the format expected by the corresponding batch command:

#### DNS Records (dns.json)

```json
[
  {
    "type": "A",
    "name": "@",
    "content": "192.0.2.1",
    "ttl": 600
  },
  {
    "type": "CNAME",
    "name": "www",
    "content": "example.com",
    "ttl": 600
  }
]
```

#### Email Forwards (email_forwards.json)

```json
[
  {
    "email_prefix": "info",
    "forward_to": "contact@example.com"
  },
  {
    "email_prefix": "sales",
    "forward_to": "sales@example.com"
  }
]
```

#### URL Forwards (url_forwards.json)

```json
[
  {
    "source": "blog",
    "destination": "https://example.com/blog",
    "type": "301"
  },
  {
    "source": "shop",
    "destination": "https://shop.example.com",
    "type": "302"
  }
]
```

## Export Configuration

The `export-config` command exports the current configuration of a domain to JSON files that can be used with the `setup-domain` command or individually with other commands.

```bash
python -m porkbun.cli workflow export-config DOMAIN [OPTIONS]
```

**Arguments:**
- `DOMAIN`: The domain to export configuration from

**Options:**
- `--dns-types TYPE...`: DNS record types to include (e.g., A, AAAA, CNAME)
- `--include-email/--exclude-email`: Include or exclude email forwards (default: include)
- `--include-url/--exclude-url`: Include or exclude URL forwards (default: include)
- `--output-dir PATH`: Directory to save configuration files (default: current directory)

### Example

Export all configuration for a domain:

```bash
python -m porkbun.cli workflow export-config example.com --output-dir ./configs
```

Export only specific DNS record types:

```bash
python -m porkbun.cli workflow export-config example.com --dns-types A CNAME MX --exclude-email --exclude-url
```

## Common Use Cases

### Migrating Domains

When moving a domain from one provider to Porkbun, you can export the configuration from the old provider, convert it to the Porkbun format, and then use `setup-domain` to apply it all at once.

### Creating Development Environments

Create separate configuration files for development, staging, and production environments, then apply them as needed:

```bash
# Set up development environment
python -m porkbun.cli workflow setup-domain dev.example.com --dns-records dev_dns.json --email-forwards dev_email.json

# Set up production environment
python -m porkbun.cli workflow setup-domain example.com --dns-records prod_dns.json --email-forwards prod_email.json
```

### Creating Domain Templates

Create template configuration files for common domain setups (e.g., business websites, blogs, e-commerce sites) and apply them to new domains:

```bash
python -m porkbun.cli workflow setup-domain new-business.com --dns-records templates/business_dns.json --email-forwards templates/business_email.json
```

## Tips and Best Practices

1. **Test Configuration Files**: Before running `setup-domain` on a production domain, validate your configuration files to ensure they contain the correct settings.

2. **Use Version Control**: Keep your domain configuration files in version control to track changes and easily roll back if needed.

3. **Backup Before Changes**: Always export the current configuration before making major changes to a domain.

4. **Use Sequential Mode for Complex Setups**: For complex domain setups or when the order of operations matters, use the sequential mode to ensure operations are completed in order.

5. **Organize Configuration Files**: Use a consistent naming scheme and directory structure for your configuration files to easily find what you need.

## Service Templates

To simplify common domain setups, the Porkbun CLI provides pre-configured DNS templates for popular services. These templates can be used with the `setup-domain` command to quickly configure a domain for use with these services.

### Available Service Templates

The following service templates are available in the `examples/templates/` directory:

- `cloudflare_dns.json` - DNS configuration for Cloudflare
- `google_workspace.json` - DNS configuration for Google Workspace (formerly G Suite)
- `office365.json` - DNS configuration for Microsoft Office 365
- `netlify.json` - DNS configuration for Netlify-hosted websites
- `aws_route53.json` - DNS configuration for AWS services
- `github_pages.json` - DNS configuration for GitHub Pages
- `vercel.json` - DNS configuration for Vercel deployments

### Using Service Templates

You can use these templates directly with the `setup-domain` command:

```bash
python -m porkbun.cli workflow setup-domain example.com --dns-records examples/templates/office365.json
```

However, these templates contain placeholder values that need to be customized for your domain. The CLI provides a helper script to simplify this process.

### Helper Script for Service Templates

The `setup_domain_services.py` script automates the process of customizing and applying service templates:

```bash
python examples/setup_domain_services.py example.com --service microsoft
```

This will:
1. Customize the service template for your domain
2. Save the customized template to a file
3. Apply the template to your domain using the `setup-domain` command

#### Available Options

- `--service`: Service to configure (choices: cloudflare, google, microsoft, all)
- `--output-dir`: Directory to save configuration files
- `--dry-run`: Preview changes without applying them

#### Examples

```bash
# Set up a domain with Google Workspace
python examples/setup_domain_services.py example.com --service google

# Preview changes for Microsoft Office 365
python examples/setup_domain_services.py example.com --service microsoft --dry-run

# Set up a domain with all service templates
python examples/setup_domain_services.py example.com --service all
```

For more detailed information on using service templates, see the [Domain Setup Guide](domain_setup.md). 