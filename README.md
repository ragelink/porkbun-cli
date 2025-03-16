# Porkbun CLI

A powerful command-line interface tool for managing domains, DNS records, SSL certificates, and more using the Porkbun API.

## Features

- **Domain Management**: List, check availability, register, transfer, renew, and manage domains
- **DNS Management**: Create, retrieve, update, and delete DNS records
- **DNSSEC Management**: Enable, disable, and check DNSSEC status
- **SSL Management**: Generate and retrieve SSL certificates
- **Account Management**: Check balance, view transaction history
- **Domain Portfolio**: Organize domains with groups and tags
- **Domain Monitoring**: Track expiring domains and price watch
- **Email Forwarding**: Set up and manage email forwards
- **URL Forwarding**: Manage URL forwards for your domains

## Requirements

- Python 3.8 or higher
- Porkbun account with API access enabled

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/porkbun-cli.git
   cd porkbun-cli
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install in development mode:
   ```bash
   pip install -e .
   ```

## Configuration

You need to set up your Porkbun API credentials. The CLI supports multiple profiles.

### API Credentials

To use the Porkbun CLI, you need to provide your Porkbun API credentials. You can do this in several ways:

1. Create a `.env` file in the root directory of the project (recommended for development):
   ```
   PORKBUN_API_KEY=your_api_key_here
   PORKBUN_SECRET_API_KEY=your_secret_api_key_here
   ```

2. Set environment variables before running the CLI:
   ```
   export PORKBUN_API_KEY=your_api_key_here
   export PORKBUN_SECRET_API_KEY=your_secret_api_key_here
   ```

3. Provide the credentials directly through the CLI:
   ```
   porkbun --api-key your_api_key_here --secret-api-key your_secret_api_key_here [command]
   ```

See the `.env.example` file for more configuration options.

### API Access Setup

1. Log in to your Porkbun account
2. Go to "Account" → "API Access"
3. Create a new API key and save both the API key and Secret key
4. Enable API access for each domain you want to manage

### Configure the CLI

```bash
# Add a new profile
python -m porkbun.cli config add default --api-key YOUR_API_KEY --secret-key YOUR_SECRET_KEY --make-default

# List profiles
python -m porkbun.cli config list

# Switch profiles
python -m porkbun.cli config use profile_name
```

## Usage

Activate your virtual environment if not already active:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Testing API Connectivity

```bash
python -m porkbun.cli account ping
```

### Domain Management

List all domains:
```bash
python -m porkbun.cli domains list-all
```

Check domain availability:
```bash
python -m porkbun.cli domains check example.com
```

Check domain with price comparison and suggestions:
```bash
python -m porkbun.cli domains check example.com --suggest --compare
```

Register a domain:
```bash
python -m porkbun.cli domains register example.com --years 1
```

Bulk register domains:
```bash
python -m porkbun.cli domains bulk domain1.com domain2.com --years 1
```

Add domain to price watch list:
```bash
python -m porkbun.cli domains check example.com --watch 9.99
```

View watch list:
```bash
python -m porkbun.cli domains watch-list
```

Check WHOIS information:
```bash
python -m porkbun.cli domains whois example.com
```

### DNS Management

List DNS records:
```bash
python -m porkbun.cli dns retrieve example.com
```

Create DNS record:
```bash
python -m porkbun.cli dns create-record example.com A 192.168.1.1 600
```

Delete DNS record:
```bash
python -m porkbun.cli dns delete-record example.com RECORD_ID
```

Check DNSSEC status:
```bash
python -m porkbun.cli dns dnssec status example.com
```

Enable DNSSEC:
```bash
python -m porkbun.cli dns dnssec enable example.com
```

### SSL Management

Retrieve SSL certificate:
```bash
python -m porkbun.cli ssl retrieve example.com
```

Generate new SSL certificate:
```bash
python -m porkbun.cli ssl generate example.com
```

### Account Management

Check account balance:
```bash
python -m porkbun.cli account balance
```

View recent transactions:
```bash
python -m porkbun.cli account transactions --limit 5
```

### Domain Portfolio Management

List domains with tags/groups:
```bash
python -m porkbun.cli account portfolio list-domains
```

Tag domains:
```bash
python -m porkbun.cli account portfolio tag example.com --group clients --tags "important,client1"
```

View all domain groups:
```bash
python -m porkbun.cli account portfolio groups
```

View all domain tags:
```bash
python -m porkbun.cli account portfolio tags
```

## URL Forwarding

The CLI supports URL forwarding management for your domains:

```bash
# List all URL forwards for a domain
python -m porkbun.cli url list-forwards example.com

# Add a URL forward
python -m porkbun.cli url add-forward example.com blog https://medium.com/@yourusername --type 301

# Delete a URL forward
python -m porkbun.cli url delete-forward example.com blog

# Add multiple URL forwards from a JSON file
python -m porkbun.cli url batch-add example.com url_forwards.json
```

URL forwarding allows you to redirect requests from paths on your domain to other URLs. This is useful for:

- Setting up redirects for legacy pages
- Creating shortcuts to external content
- Implementing a simple URL shortener
- Embedding external content in iframes

## Email Forwarding

The CLI supports email forwarding management for your domains:

```bash
# List all email forwards for a domain
python -m porkbun.cli email list-forwards example.com

# Create an email forward
python -m porkbun.cli email create-forward example.com info contact@example.com

# Update an email forward destination
python -m porkbun.cli email update-forward example.com FORWARD_ID new-email@example.com

# Delete an email forward
python -m porkbun.cli email delete-forward example.com FORWARD_ID

# Create multiple email forwards from a JSON file
python -m porkbun.cli email batch-create example.com email_forwards.json

# Delete multiple email forwards at once
python -m porkbun.cli email batch-delete example.com FORWARD_ID_1 FORWARD_ID_2 FORWARD_ID_3
```

Email forwarding allows you to receive emails sent to addresses on your domain at another email address. This is useful for:

- Creating role-based emails (info@, sales@, support@)
- Setting up email aliases without managing a full email server
- Maintaining professional email addresses that forward to personal inboxes
- Creating temporary or special-purpose email addresses

The batch operations support JSON files with the following structure:

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

## Why We Created This

We love [Porkbun](https://porkbun.com/) and created this CLI tool to make it even easier to work with their excellent domain registration and management services. Porkbun's commitment to providing a robust API enables us to build tools that enhance the domain management experience. We encourage more companies in the domain and hosting space to follow Porkbun's example by offering comprehensive APIs, which will improve the ecosystem and empower the community to create innovative solutions.

## Disclaimer

This project was developed with the assistance of AI tools, including Claude. While we've made every effort to ensure the code is reliable and secure, users should exercise caution and use this software at their own risk. We recommend testing commands in a controlled environment before using them with production domains.

## DNS Batch Operations

The CLI now supports batch operations for DNS records, allowing you to create, update, or delete multiple records in a single command.

### Batch Update DNS Records

You can create or update multiple DNS records at once using a JSON file:

```bash
porkbun dns batch-update example.com records.json
```

The JSON file should contain an array of DNS record objects with the following fields:
- `type`: Record type (A, AAAA, MX, CNAME, TXT, NS, etc.)
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

**Note on domain names**: When specifying record names, be aware that the Porkbun API may append the domain to the record name. For example, a record name of `www` might be displayed as `www.example.com.example.com` in the API response. The CLI attempts to handle this properly, but you may need to manually correct record names in some cases.

### Batch Delete DNS Records

You can delete multiple DNS records at once by specifying their IDs:

```bash
porkbun dns batch-delete example.com id1 id2 id3
```

This will delete all the specified records and provide a summary of the operation.

## Docker

To run the CLI in a Docker container:

1. Build the Docker image:
   ```bash
   docker build -t porkbun-cli .
   ```

2. Run the Docker container:
   ```bash
   docker run -v ~/.porkbun:/root/.porkbun porkbun-cli config list
   ```

3. Run commands:
   ```bash
   docker run -v ~/.porkbun:/root/.porkbun porkbun-cli domains list-all
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -r requirements-dev.txt`)
4. Make your changes
5. Run tests (`pytest`)
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Workflow Automation

The CLI provides powerful workflow automation for common domain setup tasks:

```bash
# Set up a new domain with default DNS records
python -m porkbun.cli workflow setup-domain example.com --dns-records dns_template.json

# Run a batch file with multiple commands
python -m porkbun.cli batch run services_setup.yaml --domain example.com
```

### Service Templates

Included service templates make it easy to set up domains with popular services:

- **Cloudflare DNS** - Basic DNS configuration for Cloudflare
- **Google Workspace** - DNS configuration for Google Workspace (formerly G Suite)
- **Microsoft Office 365** - DNS configuration for Microsoft Office 365
- **Netlify** - DNS configuration for Netlify-hosted websites
- **AWS Route 53** - DNS configuration for AWS services
- **GitHub Pages** - DNS configuration for GitHub Pages
- **Vercel** - DNS configuration for Vercel deployments
- **Shopify** - DNS configuration for Shopify e-commerce stores
- **Digital Ocean** - DNS configuration for Digital Ocean droplets
- **Firebase** - DNS configuration for Firebase-hosted apps

Use the helper script to set up a domain with service templates:

```bash
# Set up a domain with Microsoft Office 365 DNS records
python examples/setup_domain_services.py example.com --service microsoft

# Set up a domain with all available service templates
python examples/setup_domain_services.py example.com --service all --dry-run
```

For detailed documentation on domain setup with service templates, see [Domain Setup Guide](docs/domain_setup.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
