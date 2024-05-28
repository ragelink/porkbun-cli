import click
from porkbun.api import make_request

@click.group()
def domains():
    """Domain management commands"""
    pass

# List all domains
@domains.command()
def list_all():
    """List all domains"""
    result = make_request("domain/listAll", {})
    click.echo(result)

# Create a new domain
@domains.command()
@click.argument("domain")
@click.argument("password")
def create(domain, password):
    """Create a new domain"""
    data = {"domain": domain, "password": password}
    result = make_request("domain/create", data)
    click.echo(result)

# Delete a domain
@domains.command()
@click.argument("domain")
def delete(domain):
    """Delete a domain"""
    data = {"domain": domain}
    result = make_request("domain/delete", data)
    click.echo(result)

# Update name servers for a domain
@domains.command()
@click.argument("domain")
@click.argument("nameservers", nargs=-1)
def update_name_servers(domain, nameservers):
    """Update name servers for a domain"""
    data = {"domain": domain, "nameservers": list(nameservers)}
    result = make_request("domain/updateNameServers", data)
    click.echo(result)

# Retrieve name servers for a domain
@domains.command()
@click.argument("domain")
def retrieve_name_servers(domain):
    """Retrieve name servers for a domain"""
    data = {"domain": domain}
    result = make_request("domain/retrieveNameServers", data)
    click.echo(result)

# List contacts for a domain
@domains.command()
@click.argument("domain")
def list_contacts(domain):
    """List domain contacts"""
    data = {"domain": domain}
    result = make_request("domain/listContacts", data)
    click.echo(result)

# Update contacts for a domain
@domains.command()
@click.argument("domain")
@click.argument("contacts", nargs=-1)
def update_contacts(domain, contacts):
    """Update domain contacts"""
    data = {"domain": domain, "contacts": list(contacts)}
    result = make_request("domain/updateContacts", data)
    click.echo(result)