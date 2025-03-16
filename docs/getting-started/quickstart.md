# Quick Start Guide

This guide will help you get started with the Porkbun CLI quickly.

## Installation

Install the Porkbun CLI:

```bash
pip install porkbun-cli
```

## Configuration

Set up your API credentials:

```bash
porkbun config add default --api-key YOUR_API_KEY --secret-key YOUR_SECRET_KEY --make-default
```

## Basic Commands

### Check Connection

Test your API connection:

```bash
porkbun account ping
```

### List Your Domains

View all domains in your account:

```bash
porkbun domains list-all
```

### Check Domain Availability

Check if a domain is available for registration:

```bash
porkbun domains check example.com
```

Check multiple TLDs for a domain name:

```bash
porkbun domains check example --tlds com,net,org,io
```

### DNS Management

List DNS records for a domain:

```bash
porkbun dns retrieve example.com
```

Create a new DNS record:

```bash
porkbun dns create-record example.com A 192.168.1.1 600
```

### Service Templates

Set up a domain with a service (e.g., Google Workspace):

```bash
porkbun workflow setup-domain example.com --service google
```

## Automation Examples

### Batch Operations

Batch update multiple DNS records:

```bash
porkbun batch run examples/dns_updates.yaml
```

### Workflows

Run a predefined workflow:

```bash
porkbun workflow setup-domain example.com
```

## Getting Help

Display all available commands:

```bash
porkbun --help
```

Get help on a specific command:

```bash
porkbun domains --help
```

## Next Steps

- Explore the [Commands Reference](../api/commands.md) for a complete list of commands
- Check out the [Domain Management Guide](../user-guide/domains/checking.md) for more domain operations
- Learn about [DNS Management](../user-guide/dns/records.md) for advanced DNS operations
- See [Service Templates](../service_templates.md) for setting up domains with popular services 