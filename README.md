# Porkbun CLI

Porkbun CLI is a command-line interface tool for managing domains, DNS records, email forwards, SSL certificates, and account details using the Porkbun API.

## Features

- **Domain Management**: List, create, delete, and update domains and their name servers.
- **DNS Management**: Create, retrieve, update, and delete DNS records.
- **Email Forwarding**: Manage email forwards for domains.
- **SSL Management**: Retrieve SSL bundles for domains.
- **Account Management**: Get account details.
- **WHOIS Privacy**: Enable, disable, and retrieve WHOIS privacy status.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/porkbun-cli.git
   cd porkbun-cli
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables:
   ```bash
   export PORKBUN_API_KEY='your_api_key'
   export PORKBUN_SECRET_API_KEY='your_secret_api_key'
   ```

## Usage

### General Usage

Activate the virtual environment if not already active:
source venv/bin/activate

Run the CLI:
python -m porkbun.cli

### Commands

#### Domain Management
- List all domains: `python -m porkbun.cli domains list_all`
- Create a domain: `python -m porkbun.cli domains create <domain> <password>`
- Delete a domain: `python -m porkbun.cli domains delete <domain>`
- Update name servers: `python -m porkbun.cli domains update_name_servers <domain> <nameserver1> <nameserver2> ...`
- Retrieve name servers: `python -m porkbun.cli domains retrieve_name_servers <domain>`
- List domain contacts: `python -m porkbun.cli domains list_contacts <domain>`
- Update domain contacts: `python -m porkbun.cli domains update_contacts <domain> <contact1> <contact2> ...`

#### DNS Management
- Create a DNS record: `python -m porkbun.cli dns create_record <domain> <record_type> <content> <ttl>`
- Retrieve DNS records: `python -m porkbun.cli dns create_record <domain> <record_type> <content> <ttl>`
- Update a DNS record: `python -m porkbun.cli dns update_record <domain> <record_id> <record_type> <content> <ttl>`
- Delete a DNS record: `python -m porkbun.cli dns delete_record <domain> <record_id>`

#### Email Forwarding
- Create an email forward: `python -m porkbun.cli email create_forward <domain> <email> <forward_to>`
- Retrieve email forwards: `python -m porkbun.cli email retrieve_forwards <domain>`
- Update an email forward: `python -m porkbun.cli email update_forward <domain> <email_id> <email> <forward_to>`
- Delete an email forward: `python -m porkbun.cli email delete_forward <domain> <email_id>`

#### SSL Management
- Retrieve SSL bundle: `python -m porkbun.cli ssl retrieve_bundle <domain>`

#### Account Management
- Get account details: `python -m porkbun.cli account details`

#### WHOIS Privacy
- Enable WHOIS privacy: `python -m porkbun.cli whois enable_privacy <domain>`
- Disable WHOIS privacy: `python -m porkbun.cli whois disable_privacy <domain>`
- Retrieve WHOIS privacy status: `python -m porkbun.cli whois disable_privacy <domain>`

## Docker
To run the CLI in a Docker container:

1.	Build the Docker image:
   ```bash
   docker build -t porkbun-cli .
   ```

2.	Run the Docker container: 
   ```bash
   docker run -e PORKBUN_API_KEY='your_api_key' -e PORKBUN_SECRET_API_KEY='your_secret_api_key' porkbun-cli <command>
   ```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

CLI implementation based on [[ PorkBun Api Docs V3 - Beta | https://porkbun.com/api/json/v3/documentation#Domain%20Update%20Name%20Servers ]]

## License
This project is licensed under the MIT License. See the LICENSE file for details.
