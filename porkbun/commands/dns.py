import click
from porkbun.api import make_request

@click.group()
def dns():
    """DNS management commands"""
    pass

# Retrieve DNS records for a domain
@dns.command()
@click.argument("domain")
def retrieve(domain):
    """Retrieve DNS records for a domain"""
    result = make_request(f"dns/retrieve/{domain}", {})
    click.echo(result)

# Create a new DNS record
@dns.command()
@click.argument("domain")
@click.argument("record_type")
@click.argument("content")
@click.argument("ttl")
def create_record(domain, record_type, content, ttl):
    """Create a new DNS record"""
    data = {"domain": domain, "type": record_type, "content": content, "ttl": ttl}
    result = make_request("dns/create", data)
    click.echo(result)

# Retrieve DNS records for a domain
@dns.command()
@click.argument("domain")
def retrieve_records(domain):
    """Retrieve DNS records for a domain"""
    data = {"domain": domain}
    result = make_request("dns/retrieve", data)
    click.echo(result)

# Update a DNS record
@dns.command()
@click.argument("domain")
@click.argument("record_id")
@click.argument("record_type")
@click.argument("content")
@click.argument("ttl")
def update_record(domain, record_id, record_type, content, ttl):
    """Update a DNS record"""
    data = {"domain": domain, "id": record_id, "type": record_type, "content": content, "ttl": ttl}
    result = make_request("dns/update", data)
    click.echo(result)

# Delete a DNS record
@dns.command()
@click.argument("domain")
@click.argument("record_id")
def delete_record(domain, record_id):
    """Delete a DNS record"""
    data = {"domain": domain, "id": record_id}
    result = make_request("dns/delete", data)
    click.echo(result)