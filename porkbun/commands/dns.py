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
                console.print("[bold yellow]No DNS records found for[/] [bold green]{}[/]".format(domain))
                return 0
                
            # Sort records by type and then by name for better organization
            records = sorted(records, key=lambda r: (r.get('type', ''), r.get('name', '')))
                
            table = Table(title=f"DNS Records for [bold]{domain}[/]", title_style="bold blue", header_style="bold")
            table.add_column("Type", style="cyan", justify="center")
            table.add_column("Name", style="green")
            table.add_column("Content", style="yellow", no_wrap=False, overflow="fold")
            table.add_column("TTL", justify="right", style="magenta")
            table.add_column("ID", style="dim")
            
            # Define priority record types for highlighting
            priority_types = {"A", "AAAA", "MX", "CNAME", "TXT", "NS"}
            
            for record in records:
                record_type = record.get('type', '')
                row_style = "bold" if record_type in priority_types else ""
                
                # Format TTL with human-readable time
                ttl = int(record.get('ttl', 0))
                if ttl >= 86400:
                    ttl_display = f"{ttl//86400}d {(ttl%86400)//3600}h"
                elif ttl >= 3600:
                    ttl_display = f"{ttl//3600}h {(ttl%3600)//60}m"
                elif ttl >= 60:
                    ttl_display = f"{ttl//60}m {ttl%60}s"
                else:
                    ttl_display = f"{ttl}s"
                
                table.add_row(
                    record_type,
                    record.get('name', ''),
                    record.get('content', ''),
                    ttl_display,
                    record.get('id', ''),
                    style=row_style
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
                console.print("[bold yellow]No DNS records found for[/] [bold green]{}[/]".format(domain))
                return 0
                
            # Sort records by type and then by name for better organization
            records = sorted(records, key=lambda r: (r.get('type', ''), r.get('name', '')))
                
            table = Table(title=f"DNS Records for [bold]{domain}[/]", title_style="bold blue", header_style="bold")
            table.add_column("Type", style="cyan", justify="center")
            table.add_column("Name", style="green")
            table.add_column("Content", style="yellow", no_wrap=False, overflow="fold")
            table.add_column("TTL", justify="right", style="magenta")
            table.add_column("ID", style="dim")
            
            # Define priority record types for highlighting
            priority_types = {"A", "AAAA", "MX", "CNAME", "TXT", "NS"}
            
            for record in records:
                record_type = record.get('type', '')
                row_style = "bold" if record_type in priority_types else ""
                
                # Format TTL with human-readable time
                ttl = int(record.get('ttl', 0))
                if ttl >= 86400:
                    ttl_display = f"{ttl//86400}d {(ttl%86400)//3600}h"
                elif ttl >= 3600:
                    ttl_display = f"{ttl//3600}h {(ttl%3600)//60}m"
                elif ttl >= 60:
                    ttl_display = f"{ttl//60}m {ttl%60}s"
                else:
                    ttl_display = f"{ttl}s"
                
                table.add_row(
                    record_type,
                    record.get('name', ''),
                    record.get('content', ''),
                    ttl_display,
                    record.get('id', ''),
                    style=row_style
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
        result = asyncio.run(make_request(f"dns/delete/{domain}/{record_id}", {}))
        if result.get('status') == 'SUCCESS':
            console.print(f"[green]Successfully deleted record ID: {record_id}[/]")
        else:
            console.print(f"[error]Failed to delete record: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)

# Batch delete DNS records
@dns.command()
@click.argument("domain")
@click.argument("record_ids", nargs=-1)
def batch_delete(domain, record_ids):
    """Delete multiple DNS records at once"""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    if not record_ids:
        console.print("[error]No record IDs provided. Please specify at least one record ID to delete.[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
        
    success_count = 0
    error_count = 0
    
    with console.status(f"[bold green]Deleting {len(record_ids)} DNS records from {domain}...[/]") as status:
        for i, record_id in enumerate(record_ids):
            status.update(f"[bold green]Deleting record {i+1}/{len(record_ids)}: ID {record_id}[/]")
            
            try:
                result = asyncio.run(make_request(f"dns/delete/{domain}/{record_id}", {}))
                if result.get('status') == 'SUCCESS':
                    console.print(f"[green]Successfully deleted record ID: {record_id}[/]")
                    success_count += 1
                else:
                    console.print(f"[error]Failed to delete record {record_id}: {result.get('message', 'Unknown error')}[/]")
                    error_count += 1
            except Exception as e:
                console.print(f"[error]Error deleting record {record_id}: {str(e)}[/]")
                error_count += 1
    
    # Summary
    if success_count > 0 and error_count == 0:
        console.print(f"[bold green]Successfully deleted all {success_count} DNS records from {domain}[/]")
    elif success_count > 0:
        console.print(f"[bold yellow]Deleted {success_count} records successfully with {error_count} errors from {domain}[/]")
    else:
        console.print(f"[bold red]Failed to delete any DNS records from {domain}[/]")

# Batch update DNS records for a domain
@dns.command()
@click.argument("domain")
@click.argument("batch_file", type=click.Path(exists=True, readable=True))
def batch_update(domain, batch_file):
    """Batch update DNS records for a domain using a JSON file.
    
    The JSON file should contain an array of DNS record objects with the following fields:
    - type: Record type (A, AAAA, MX, CNAME, TXT, NS, etc.)
    - name: Record name
    - content: Record content
    - ttl: Time to live (optional, defaults to 600)
    - id: Record ID (only needed for updating existing records)
    
    Example JSON file:
    [
        {"type": "A", "name": "example.com", "content": "192.0.2.1", "ttl": 600},
        {"type": "CNAME", "name": "www.example.com", "content": "example.com", "ttl": 600}
    ]
    """
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        # Read batch file
        with open(batch_file, 'r') as f:
            records = json.load(f)
            
        if not isinstance(records, list):
            console.print("[error]Batch file must contain a JSON array of DNS record objects[/]")
            ctx = click.get_current_context()
            ctx.exit(1)
            
        # Get existing records to compare and update
        result = asyncio.run(make_request(f"dns/retrieve/{domain}", {}))
        if result.get('status') != 'SUCCESS':
            console.print(f"[error]Error retrieving existing DNS records: {result.get('message', 'Unknown error')}[/]")
            ctx = click.get_current_context()
            ctx.exit(1)
            
        existing_records = {r.get('id'): r for r in result.get('records', [])}
        
        # Process each record
        success_count = 0
        error_count = 0
        
        with console.status(f"[bold green]Processing {len(records)} DNS records for {domain}...[/]") as status:
            for i, record in enumerate(records):
                record_id = record.get('id')
                record_type = record.get('type')
                record_name = record.get('name')
                record_content = record.get('content')
                record_ttl = record.get('ttl', 600)
                
                # Validate record
                if not record_type or not record_name or not record_content:
                    console.print(f"[error]Record {i+1}: Missing required fields (type, name, content)[/]")
                    error_count += 1
                    continue
                    
                try:
                    validate_record_type(record_type)
                    validate_ttl(record_ttl)
                except click.BadParameter as e:
                    console.print(f"[error]Record {i+1}: {str(e)}[/]")
                    error_count += 1
                    continue
                
                status.update(f"[bold green]Processing record {i+1}/{len(records)}: {record_type} {record_name}[/]")
                
                # Normalize record name to avoid domain duplication
                if record_name == "@" or record_name == "":
                    # Root domain
                    record_name = domain
                elif record_name.endswith(f".{domain}"):
                    # Strip duplicate domain suffix if present
                    if record_name == f"{domain}.{domain}":
                        record_name = domain
                    else:
                        # Already has domain suffix
                        pass
                elif "." not in record_name:
                    # Single label, add domain
                    record_name = f"{record_name}.{domain}"
                else:
                    # Multi-label that doesn't end with the domain
                    if not record_name.endswith("."):
                        # Not a fully qualified domain name, treat as relative to the domain
                        if not domain in record_name:
                            record_name = f"{record_name}.{domain}"
                
                console.print(f"[dim]Using normalized name: {record_name}[/]")
                
                # Create or update record
                if record_id and record_id in existing_records:
                    # Update existing record
                    endpoint = f"dns/edit/{domain}/{record_id}"
                    data = {
                        "type": record_type,
                        "name": record_name,
                        "content": record_content,
                        "ttl": record_ttl
                    }
                    update_result = asyncio.run(make_request(endpoint, data))
                    if update_result.get('status') == 'SUCCESS':
                        console.print(f"[green]Updated record: {record_type} {record_name}[/]")
                        success_count += 1
                    else:
                        console.print(f"[error]Failed to update record {record_name}: {update_result.get('message', 'Unknown error')}[/]")
                        error_count += 1
                else:
                    # Create new record
                    endpoint = f"dns/create/{domain}"
                    data = {
                        "type": record_type,
                        "name": record_name,
                        "content": record_content,
                        "ttl": record_ttl
                    }
                    create_result = asyncio.run(make_request(endpoint, data))
                    if create_result.get('status') == 'SUCCESS':
                        console.print(f"[green]Created record: {record_type} {record_name}[/]")
                        success_count += 1
                    else:
                        console.print(f"[error]Failed to create record {record_name}: {create_result.get('message', 'Unknown error')}[/]")
                        error_count += 1
        
        # Summary
        if success_count > 0 and error_count == 0:
            console.print(f"[bold green]Successfully processed all {success_count} DNS records for {domain}[/]")
        elif success_count > 0:
            console.print(f"[bold yellow]Processed {success_count} records successfully with {error_count} errors for {domain}[/]")
        else:
            console.print(f"[bold red]Failed to process any DNS records for {domain}[/]")
            
        return 0
    except json.JSONDecodeError:
        console.print(f"[error]Invalid JSON in batch file {batch_file}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")
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