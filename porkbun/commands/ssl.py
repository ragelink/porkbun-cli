import click
from porkbun.api import make_request

@click.group()
def ssl():
    """SSL management commands"""
    pass

# Retrieve SSL bundle for a domain
@ssl.command()
@click.argument("domain")
def retrieve_bundle(domain):
    """Retrieve SSL bundle for a domain"""
    data = {"domain": domain}
    result = make_request("ssl/retrieve", data)
    click.echo(result)