# Domain Setup with Multiple Services

This guide explains how to use the Porkbun CLI to set up a domain with multiple service configurations using our helper scripts and templates.

## Available Tools

The Porkbun CLI provides several tools to simplify domain setup:

1. **Service Templates** - Pre-configured DNS records for popular services
2. **Template Customization Tool** - Script to personalize templates for your domain
3. **Domain Setup Script** - Tool to apply service configurations to your domain

## Service Templates

Templates for the following services are available:

- **Cloudflare DNS** - Basic DNS configuration for Cloudflare
- **Google Workspace** - DNS configuration for Google Workspace (formerly G Suite)
- **Microsoft Office 365** - DNS configuration for Microsoft Office 365

Templates are located in the `examples/templates/` directory.

## Using the Setup Script

The `setup_domain_services.py` script automates the process of applying service configurations to your domain.

### Basic Usage

```bash
python examples/setup_domain_services.py yourdomain.com --service cloudflare
```

### Available Options

- `--service` - Service to configure (choices: cloudflare, google, microsoft, all)
- `--output-dir` - Directory to save configuration files
- `--dry-run` - Preview changes without applying them

### Examples

**Setup with Google Workspace:**
```bash
python examples/setup_domain_services.py yourdomain.com --service google
```

**Setup with multiple services:**
```bash
python examples/setup_domain_services.py yourdomain.com --service all
```

**Preview changes:**
```bash
python examples/setup_domain_services.py yourdomain.com --service microsoft --dry-run
```

## Manual Template Customization

If you need to customize templates manually:

1. Use the `customize_template.py` script:
   ```bash
   python examples/customize_template.py examples/templates/office365.json yourdomain.com
   ```

2. Apply the customized template:
   ```bash
   python -m porkbun.cli workflow setup-domain yourdomain.com --dns-records yourdomain.com_office365.json
   ```

## Important Notes

- Always review generated DNS records before applying them to production domains
- Some services may require additional verification steps not handled by these templates
- Manual customization may be needed for specific use cases
- Templates contain placeholder values that will be replaced with your domain name

## Troubleshooting

If you encounter issues:

1. Verify that your Porkbun API credentials are correctly configured
2. Check that the domain exists in your Porkbun account
3. Review the generated configuration files for any inconsistencies
4. Use the `--dry-run` option to preview changes before applying them 