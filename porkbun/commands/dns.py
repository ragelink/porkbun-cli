import click
import json
from porkbun.api import make_request
from porkbun.utils.exceptions import PorkbunAPIError
from porkbun.utils.validation import validate_domain, validate_ip_address, validate_ttl, validate_record_type

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
        result = make_request(f"dns/retrieve/{domain}", {})
        click.echo(result)
        return 0
    except PorkbunAPIError as e:
        click.echo(f"Error: {str(e)}")
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
        data = {"domain": domain}
        result = make_request("dns/retrieve", data)
        click.echo(result)
        return 0
    except PorkbunAPIError as e:
        click.echo(f"Error: {str(e)}")
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