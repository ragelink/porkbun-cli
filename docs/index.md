# Porkbun CLI Documentation

Welcome to the Porkbun CLI documentation! This powerful command-line tool helps you manage your Porkbun domains and services efficiently.

## Features

### 🌐 Domain Management
- Domain availability checking and suggestions
- Bulk domain registration and transfer
- Automated renewal management
- WHOIS privacy settings
- Domain price watch functionality
- Custom nameservers configuration

### 🔒 DNS Management
- Comprehensive DNS record management
- Bulk operations and templates
- DNSSEC configuration and key management
- Zone file import/export
- Formatted table output for better readability

### 🔑 SSL Certificates
- Certificate issuance and renewal
- Installation guides
- Expiration monitoring

### 📊 Account Management
- Balance checking and transaction history
- Multiple profile support
- Domain portfolio organization with tags and groups
- Email forwarding configuration

### 📈 Monitoring
- Domain expiration tracking
- DNS propagation checking
- Health monitoring
- Custom alerts

### 🤖 Automation
- Task scheduling
- Webhook integration
- Scripting support
- Batch operations

## Installation

### Requirements
- Python 3.8 or higher
- Porkbun account with API access enabled

### Step-by-Step Installation

```bash
# Clone the repository
git clone https://github.com/ragelink/porkbun-cli.git
cd porkbun-cli

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Docker Installation

```bash
# Build the Docker image
docker build -t porkbun-cli .

# Run with volume mount for configuration
docker run -v ~/.porkbun:/root/.porkbun porkbun-cli domains list-all
```

## Configuration

### API Access Setup

1. Log in to your Porkbun account
2. Navigate to "Account" → "API Access"
3. Create a new API key and save both the API key and Secret key
4. Enable API access for each domain you want to manage

### CLI Configuration

```bash
# Add a new profile
python -m porkbun.cli config add default --api-key YOUR_API_KEY --secret-key YOUR_SECRET_KEY --make-default

# List profiles
python -m porkbun.cli config list

# Switch profiles
python -m porkbun.cli config use profile_name
```

## Usage Examples

### Domain Management

```bash
# Check API connectivity
python -m porkbun.cli account ping

# List all domains
python -m porkbun.cli domains list-all

# Check domain availability with suggestions
python -m porkbun.cli domains check example.com --suggest --compare

# Register a domain
python -m porkbun.cli domains register example.com --years 1

# Add domain to price watch
python -m porkbun.cli domains check example.com --watch 9.99
```

### DNS Management

```bash
# List DNS records
python -m porkbun.cli dns retrieve example.com

# Create DNS record
python -m porkbun.cli dns create-record example.com A 192.168.1.1 600

# Manage DNSSEC
python -m porkbun.cli dns dnssec enable example.com
```

### Portfolio Management

```bash
# Tag domains
python -m porkbun.cli account portfolio tag example.com --group clients --tags "important,client1"

# View domain groups
python -m porkbun.cli account portfolio groups
```

## Getting Help

- Check the [Quick Start Guide](getting-started/quickstart.md) for basic usage
- Browse the [Commands Reference](api/commands.md) for command details
- View the [Service Templates](service_templates.md) for domain setup options
- Read the [Troubleshooting Guide](troubleshooting.md) for common issues
- Join our [GitHub Discussions](https://github.com/ragelink/porkbun-cli/discussions) for community support

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify your API keys are correct
   - Ensure the domain has API access enabled in your Porkbun account
   - Check your internet connection

2. **Command Not Found**
   - Ensure you're running the command from the correct directory
   - Verify your virtual environment is activated
   - Check that the package is installed correctly

3. **Permission Errors**
   - Make sure your API key has sufficient permissions
   - Check file permissions if working with configuration files

## Contributing

We welcome contributions! Check our [Contributing Guide](development/contributing.md) to get started.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Make your changes
5. Run tests: `pytest`
6. Commit your changes: `git commit -m 'Add some amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/ragelink/porkbun-cli/blob/main/LICENSE) file for details. 