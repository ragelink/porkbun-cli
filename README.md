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

## License

This project is licensed under the MIT License - see the LICENSE file for details.
