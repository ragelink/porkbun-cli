import click
import json
import asyncio
from porkbun.api import make_request
from porkbun.utils.exceptions import PorkbunAPIError
from porkbun.utils.validation import validate_domain, validate_ip_address, validate_ttl, validate_record_type
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def dns():
    """DNS management commands"""
    pass

# Retrieve DNS records for a domain
@dns.command()
@click.argument("domain")
def retrieve(domain):
    """Retrieve DNS records for a domain"""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        result = asyncio.run(make_request(f"dns/retrieve/{domain}", {}))
        if result.get('status') == 'SUCCESS':
            records = result.get('records', [])
            
            if not records:
                console.print("[info]No DNS records found[/]")
                return 0
                
            table = Table(title=f"DNS Records for {domain}")
            table.add_column("Type", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Content", style="yellow")
            table.add_column("TTL", justify="right")
            table.add_column("ID", style="dim")
            
            for record in records:
                table.add_row(
                    record.get('type', ''),
                    record.get('name', ''),
                    record.get('content', ''),
                    str(record.get('ttl', '')),
                    record.get('id', '')
                )
            
            console.print(table)
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
        return 0
    except PorkbunAPIError as e:
        console.print(f"[error]Error: {str(e)}[/]")
        if "domain is not opted in to api access" in str(e).lower():
            console.print("[info]This error occurs when a domain is not enabled for API access in your Porkbun account.[/]")
            console.print("[info]To fix this issue:[/]")
            console.print("[info]1. Log in to your Porkbun dashboard at https://porkbun.com/account/login[/]")
            console.print("[info]2. Navigate to the domain management page for " + domain + "[/]")
            console.print("[info]3. Look for the 'API Access' option and enable it[/]")
            console.print("[info]4. Try this command again after enabling API access[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)

def validate_ttl_callback(ctx, param, value):
    """Validate TTL value"""
    if not validate_ttl(str(value)):
        raise click.BadParameter("TTL must be a positive integer")
    return value

# Create a new DNS record
@dns.command()
@click.argument("domain")
@click.argument("record_type")
@click.argument("content")
@click.argument("ttl", type=int, callback=validate_ttl_callback)
def create_record(domain, record_type, content, ttl):
    """Create a new DNS record"""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    if not validate_record_type(record_type):
        raise click.BadParameter("Invalid record type")
        
    if record_type.upper() == 'A' and not validate_ip_address(content):
        raise click.BadParameter("Invalid IP address format")
    
    try:
        data = {"domain": domain, "type": record_type, "content": content, "ttl": str(ttl)}
        result = make_request("dns/create", data)
        click.echo(result)
        return 0
    except PorkbunAPIError as e:
        click.echo(f"Error: {str(e)}")
        ctx = click.get_current_context()
        ctx.exit(1)

# Retrieve DNS records for a domain
@dns.command()
@click.argument("domain")
def retrieve_records(domain):
    """Retrieve all DNS records for a domain"""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        result = asyncio.run(make_request(f"dns/retrieve/{domain}", {}))
        if result.get('status') == 'SUCCESS':
            records = result.get('records', [])
            
            if not records:
                console.print("[info]No DNS records found[/]")
                return 0
                
            table = Table(title=f"DNS Records for {domain}")
            table.add_column("Type", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Content", style="yellow")
            table.add_column("TTL", justify="right")
            table.add_column("ID", style="dim")
            
            for record in records:
                table.add_row(
                    record.get('type', ''),
                    record.get('name', ''),
                    record.get('content', ''),
                    str(record.get('ttl', '')),
                    record.get('id', '')
                )
            
            console.print(table)
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
        return 0
    except PorkbunAPIError as e:
        console.print(f"[error]Error: {str(e)}[/]")
        if "domain is not opted in to api access" in str(e).lower():
            console.print("[info]This error occurs when a domain is not enabled for API access in your Porkbun account.[/]")
            console.print("[info]To fix this issue:[/]")
            console.print("[info]1. Log in to your Porkbun dashboard at https://porkbun.com/account/login[/]")
            console.print("[info]2. Navigate to the domain management page for " + domain + "[/]")
            console.print("[info]3. Look for the 'API Access' option and enable it[/]")
            console.print("[info]4. Try this command again after enabling API access[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)

def validate_records_json(ctx, param, value):
    """Validate records JSON"""
    if not value:
        return None
    try:
        print(f"Validating records JSON: {value}")
        records = json.loads(value)
        if not isinstance(records, list):
            print("Not a list")
            raise click.BadParameter("Records must be a JSON array")
        for record in records:
            print(f"Validating record: {record}")
            if not isinstance(record, dict):
                print("Not a dict")
                raise click.BadParameter("Each record must be a JSON object")
            if not all(k in record for k in ["id", "type", "content", "ttl"]):
                print("Missing required fields")
                raise click.BadParameter("Each record must have id, type, content, and ttl fields")
            if not validate_record_type(record["type"]):
                print(f"Invalid record type: {record['type']}")
                raise click.BadParameter(f"Invalid record type in record {record['id']}")
            if record["type"].upper() == 'A' and not validate_ip_address(record["content"]):
                print(f"Invalid IP address: {record['content']}")
                raise click.BadParameter(f"Invalid IP address in record {record['id']}")
            if not validate_ttl(str(record["ttl"])):
                print(f"Invalid TTL: {record['ttl']}")
                raise click.BadParameter(f"Invalid TTL in record {record['id']}")
        return records
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        raise click.BadParameter(f"Invalid JSON format in records parameter: {str(e)}")
    except (KeyError, TypeError) as e:
        print(f"Record format error: {e}")
        raise click.BadParameter(f"Invalid record format: {str(e)}")

# Update a DNS record
@dns.command()
@click.argument("domain")
@click.option("--records", callback=validate_records_json, help="JSON array of records to update in bulk")
@click.option("--record-id", help="Record ID for single record update")
@click.option("--record-type", help="Record type for single record update")
@click.option("--content", help="Record content for single record update")
@click.option("--ttl", type=int, help="TTL for single record update")
def update_record(domain, records=None, record_id=None, record_type=None, content=None, ttl=None):
    """Update DNS record(s)"""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
    
    try:
        if records:
            # Bulk update
            for record in records:
                data = {
                    "domain": domain,
                    "id": record["id"],
                    "type": record["type"],
                    "content": record["content"],
                    "ttl": record["ttl"]  # No need to convert to string, API accepts both
                }
                result = make_request("dns/update", data)
                click.echo(f"Updated record {record['id']}: {result}")
        else:
            # Single record update
            if not all([record_id, record_type, content, ttl]):
                raise click.UsageError("For single record update, all of --record-id, --record-type, --content, and --ttl are required")
                
            if not validate_record_type(record_type):
                raise click.BadParameter("Invalid record type")
                
            if record_type.upper() == 'A' and not validate_ip_address(content):
                raise click.BadParameter("Invalid IP address format")
                
            if not validate_ttl(str(ttl)):
                raise click.BadParameter("TTL must be a positive integer")
                
            data = {
                "domain": domain,
                "id": record_id,
                "type": record_type,
                "content": content,
                "ttl": str(ttl)
            }
            result = make_request("dns/update", data)
            click.echo(result)
            
        return 0
    except PorkbunAPIError as e:
        click.echo(f"Error: {str(e)}")
        ctx = click.get_current_context()
        ctx.exit(1)

# Delete a DNS record
@dns.command()
@click.argument("domain")
@click.argument("record_id")
def delete_record(domain, record_id):
    """Delete a DNS record"""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        data = {"domain": domain, "id": record_id}
        result = make_request("dns/delete", data)
        click.echo(result)
        return 0
    except PorkbunAPIError as e:
        click.echo(f"Error: {str(e)}")
        ctx = click.get_current_context()
        ctx.exit(1)

@dns.group()
def dnssec():
    """DNSSEC management commands"""
    pass

@dnssec.command()
@click.argument('domain')
def status(domain: str):
    """Check DNSSEC status for a domain."""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        result = make_request(f"dns/getDNSSEC/{domain}", {})
        if result.get('status') == 'SUCCESS':
            enabled = result.get('dnssec', False)
            status = "[green]Enabled[/]" if enabled else "[red]Disabled[/]"
            console.print(f"DNSSEC is {status} for {domain}")
            
            if enabled and result.get('keys'):
                table = Table(title="DNSSEC Keys")
                table.add_column("Type", style="cyan")
                table.add_column("Algorithm", style="blue")
                table.add_column("Key Tag", style="dim")
                table.add_column("Public Key", style="green")
                
                for key in result['keys']:
                    table.add_row(
                        key.get('type', 'N/A'),
                        key.get('algorithm', 'N/A'),
                        key.get('keyTag', 'N/A'),
                        key.get('publicKey', 'N/A')
                    )
                
                console.print(table)
        else:
            console.print(f"[error]Error checking DNSSEC status: {result.get('message')}[/]")
    except Exception as e:
        console.print(f"[error]Error checking DNSSEC status: {str(e)}[/]")

@dnssec.command()
@click.argument('domain')
def enable(domain: str):
    """Enable DNSSEC for a domain."""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        result = make_request(f"dns/enableDNSSEC/{domain}", {})
        if result.get('status') == 'SUCCESS':
            console.print(f"[success]Successfully enabled DNSSEC for {domain}[/]")
            
            # Show DS records for registrar configuration
            if result.get('dsRecords'):
                table = Table(title="DS Records (Configure these at your registrar)")
                table.add_column("Key Tag", style="cyan")
                table.add_column("Algorithm", style="blue")
                table.add_column("Digest Type", style="dim")
                table.add_column("Digest", style="green")
                
                for record in result['dsRecords']:
                    table.add_row(
                        str(record.get('keyTag', 'N/A')),
                        str(record.get('algorithm', 'N/A')),
                        str(record.get('digestType', 'N/A')),
                        record.get('digest', 'N/A')
                    )
                
                console.print(table)
                console.print("\n[warning]Important: Configure these DS records at your domain registrar to complete DNSSEC setup[/]")
        else:
            console.print(f"[error]Error enabling DNSSEC: {result.get('message')}[/]")
    except Exception as e:
        console.print(f"[error]Error enabling DNSSEC: {str(e)}[/]")

@dnssec.command()
@click.argument('domain')
def disable(domain: str):
    """Disable DNSSEC for a domain."""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        result = make_request(f"dns/disableDNSSEC/{domain}", {})
        if result.get('status') == 'SUCCESS':
            console.print(f"[success]Successfully disabled DNSSEC for {domain}[/]")
            console.print("[warning]Remember to remove DS records from your domain registrar[/]")
        else:
            console.print(f"[error]Error disabling DNSSEC: {result.get('message')}[/]")
    except Exception as e:
        console.print(f"[error]Error disabling DNSSEC: {str(e)}[/]")

@dnssec.command()
@click.argument('domain')
def rotate_keys(domain: str):
    """Rotate DNSSEC keys for a domain."""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        # First check if DNSSEC is enabled
        status_result = make_request(f"dns/getDNSSEC/{domain}", {})
        if not status_result.get('dnssec', False):
            console.print(f"[error]DNSSEC is not enabled for {domain}[/]")
            return
            
        # Disable DNSSEC
        disable_result = make_request(f"dns/disableDNSSEC/{domain}", {})
        if disable_result.get('status') != 'SUCCESS':
            console.print(f"[error]Error disabling DNSSEC: {disable_result.get('message')}[/]")
            return
            
        # Re-enable DNSSEC to generate new keys
        enable_result = make_request(f"dns/enableDNSSEC/{domain}", {})
        if enable_result.get('status') == 'SUCCESS':
            console.print(f"[success]Successfully rotated DNSSEC keys for {domain}[/]")
            
            # Show new DS records
            if enable_result.get('dsRecords'):
                table = Table(title="New DS Records (Update these at your registrar)")
                table.add_column("Key Tag", style="cyan")
                table.add_column("Algorithm", style="blue")
                table.add_column("Digest Type", style="dim")
                table.add_column("Digest", style="green")
                
                for record in enable_result['dsRecords']:
                    table.add_row(
                        str(record.get('keyTag', 'N/A')),
                        str(record.get('algorithm', 'N/A')),
                        str(record.get('digestType', 'N/A')),
                        record.get('digest', 'N/A')
                    )
                
                console.print(table)
                console.print("\n[warning]Important: Update these DS records at your domain registrar[/]")
        else:
            console.print(f"[error]Error re-enabling DNSSEC: {enable_result.get('message')}[/]")
    except Exception as e:
        console.print(f"[error]Error rotating DNSSEC keys: {str(e)}[/]")