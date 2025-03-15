# Porkbun CLI Troubleshooting Guide

This guide helps you diagnose and solve common issues when using the Porkbun CLI.

## API Connection Issues

### Problem: Authentication Failed

**Error message:** `Authentication failed`, `Invalid API key`, or `Invalid credentials`

**Possible causes:**
- Incorrect API key or Secret key
- Expired API key
- API access disabled in Porkbun account

**Solutions:**
1. Verify your API key and Secret key are correct:
   ```bash
   python -m porkbun.cli config list
   ```
2. Create a new API key in your Porkbun account and update the CLI:
   ```bash
   python -m porkbun.cli config add default --api-key NEW_KEY --secret-key NEW_SECRET --make-default
   ```
3. Check API access is enabled in your Porkbun account dashboard.

### Problem: Domain Not Authorized

**Error message:** `Domain is not opted in to API access` or `Not authorized for domain`

**Possible causes:**
- API access not enabled for the specific domain
- Domain not owned by your Porkbun account

**Solutions:**
1. Log in to your Porkbun account
2. Navigate to the domain management page for the specific domain
3. Find the "API Access" option and enable it
4. Try your command again

### Problem: Rate Limiting

**Error message:** `Too many requests` or `Rate limit exceeded`

**Possible causes:**
- Sending too many API requests in a short period
- Running multiple commands simultaneously

**Solutions:**
1. Wait a few minutes before trying again
2. Add delays between API calls in scripts
3. Check your code for unnecessary API calls in loops

## DNS Management Issues

### Problem: DNS Record Not Creating

**Error message:** `Error creating record` or `Invalid record data`

**Possible causes:**
- Invalid DNS record format
- Incorrect record type
- Duplicate record

**Solutions:**
1. Check the format of your record data
2. Verify the record type is supported (A, AAAA, CNAME, MX, TXT, etc.)
3. List existing records to check for duplicates:
   ```bash
   python -m porkbun.cli dns retrieve example.com
   ```

### Problem: Async Operation Warning

**Error message:** `Coroutine was never awaited` or similar warning

**Possible causes:**
- Bug in the DNS retrieval function

**Solutions:**
1. Update to the latest version of the CLI
2. Try using the `--json` flag which may bypass this issue:
   ```bash
   python -m porkbun.cli dns retrieve example.com --json
   ```
3. As a temporary workaround, use a direct API call:
   ```bash
   curl -X POST "https://porkbun.com/api/json/v3/dns/retrieve/{DOMAIN}" \
     -H "Content-Type: application/json" \
     -d '{"apikey":"YOUR_API_KEY","secretapikey":"YOUR_SECRET_KEY"}'
   ```

## Installation and Configuration Issues

### Problem: Command Not Found

**Error message:** `Command not found`, `ModuleNotFoundError`, or similar

**Possible causes:**
- Virtual environment not activated
- Package not installed correctly
- PATH not configured correctly

**Solutions:**
1. Ensure your virtual environment is activated:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Reinstall the package:
   ```bash
   pip install -e .
   ```
3. Verify the installation location is in your PATH

### Problem: Missing Dependencies

**Error message:** `ImportError: No module named X`

**Possible causes:**
- Missing Python package
- Incorrect Python version

**Solutions:**
1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Check your Python version:
   ```bash
   python --version  # Should be 3.8 or higher
   ```

### Problem: Configuration Not Found

**Error message:** `No configuration found` or `No profile configured`

**Possible causes:**
- Configuration file missing or corrupted
- No default profile set

**Solutions:**
1. Add a new configuration profile:
   ```bash
   python -m porkbun.cli config add default --api-key YOUR_API_KEY --secret-key YOUR_SECRET_KEY --make-default
   ```
2. Check if configuration exists:
   ```bash
   python -m porkbun.cli config list
   ```
3. Check the configuration file location:
   - Linux/macOS: `~/.porkbun/config.json`
   - Windows: `%USERPROFILE%\.porkbun\config.json`

## Docker Issues

### Problem: Configuration Persistence

**Error message:** `No configuration found` when running in Docker

**Possible causes:**
- Volume mount not set up correctly
- Permissions issue

**Solutions:**
1. Use the volume mount to persist configuration:
   ```bash
   docker run -v ~/.porkbun:/root/.porkbun porkbun-cli config list
   ```
2. Create the configuration directory first:
   ```bash
   mkdir -p ~/.porkbun
   ```
3. Check file permissions on the host directory

### Problem: Docker Command Output

**Error message:** Garbled or incomplete output from Docker

**Possible causes:**
- Terminal size issues
- TTY allocation

**Solutions:**
1. Add TTY allocation to the Docker command:
   ```bash
   docker run -it -v ~/.porkbun:/root/.porkbun porkbun-cli domains list-all
   ```
2. Use the `--json` flag for structured output:
   ```bash
   docker run -v ~/.porkbun:/root/.porkbun porkbun-cli domains list-all --json
   ```

## Debugging Techniques

### Enable Verbose Output

Add the `--verbose` flag to see detailed information about what's happening:

```bash
python -m porkbun.cli domains list-all --verbose
```

### Check API Response

Use the `--json` flag to see the raw API response:

```bash
python -m porkbun.cli account ping --json
```

### Inspect Configuration

Check your current configuration:

```bash
python -m porkbun.cli config list
```

### Check Logs

Logs are stored in:
- Linux/macOS: `~/.porkbun/logs/`
- Windows: `%USERPROFILE%\.porkbun\logs\`

### Test Network Connectivity

Test if you can reach the Porkbun API server:

```bash
curl -I https://porkbun.com/api/json/v3/ping
```

## Getting More Help

If you're still experiencing issues:

1. Check the [GitHub Issues](https://github.com/ragelink/porkbun-cli/issues) to see if your problem has been reported
2. Open a new issue with:
   - Command you're trying to run
   - Error message (full traceback if available)
   - Your operating system and Python version
   - Steps to reproduce
3. Join the community discussions for assistance 