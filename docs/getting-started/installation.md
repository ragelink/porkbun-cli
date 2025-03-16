# Installation Guide

This guide explains how to install the Porkbun CLI on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Porkbun account with API access

## Installation Methods

### From PyPI (Recommended)

The easiest way to install the Porkbun CLI is from PyPI:

```bash
pip install porkbun-cli
```

To install in a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install porkbun-cli
```

### From Source

To install from source:

```bash
# Clone the repository
git clone https://github.com/ragelink/porkbun-cli.git
cd porkbun-cli

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies and package
pip install -e .
```

### Docker Installation

For Docker users:

```bash
# Build the Docker image
docker build -t porkbun-cli .

# Run with volume mount for configuration
docker run -v ~/.porkbun:/root/.porkbun porkbun-cli --help
```

## Verify Installation

To verify that the installation was successful:

```bash
porkbun --version
```

or

```bash
python -m porkbun.cli --version
```

## Setting Up API Access

Before using the CLI, you'll need to set up your Porkbun API credentials:

1. Log in to your Porkbun account
2. Navigate to "Account" → "API Access"
3. Create a new API key and save both the API key and Secret key
4. Enable API access for each domain you want to manage

## Basic Configuration

Configure the CLI with your API credentials:

```bash
porkbun config add default --api-key YOUR_API_KEY --secret-key YOUR_SECRET_KEY --make-default
```

or

```bash
python -m porkbun.cli config add default --api-key YOUR_API_KEY --secret-key YOUR_SECRET_KEY --make-default
```

## Test the Connection

Test your API connection:

```bash
porkbun account ping
```

If successful, you'll see a success message confirming your API connection works.

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade porkbun-cli
```

## Troubleshooting

### Common Installation Issues

1. **Python Version Error**

   If you receive an error about Python version requirements, make sure you have Python 3.8 or higher installed:

   ```bash
   python --version
   ```

2. **Permission Denied**

   If you encounter permission issues during installation, try using:

   ```bash
   pip install --user porkbun-cli
   ```

3. **Package Not Found**

   If the `porkbun` command is not found after installation, ensure that your Python scripts directory is in your PATH.

### Getting Help

If you encounter any issues, check the [Troubleshooting Guide](../troubleshooting.md) or create an issue on the [GitHub repository](https://github.com/ragelink/porkbun-cli/issues). 