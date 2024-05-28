import click
from porkbun.api import make_request

@click.group()
def account():
    """Account management commands"""
    pass

# Get account details
@account.command()
def details():
    """Get account details"""
    result = make_request("account/details", {})
    click.echo(result)