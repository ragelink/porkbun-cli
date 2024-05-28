import click
from porkbun.api import make_request

@click.group()
def whois():
    """WHOIS privacy commands"""
    pass

# Enable WHOIS privacy
@whois.command()
@click.argument("domain")
def enable_privacy(domain):
    """Enable WHOIS privacy"""
    data = {"domain": domain}
    result = make_request("whois/enable", data)
    click.echo(result)

# Disable WHOIS privacy
@whois.command()
@click.argument("domain")
def disable_privacy(domain):
    """Disable WHOIS privacy"""
    data = {"domain": domain}
    result = make_request("whois/disable", data)
    click.echo(result)

# Retrieve WHOIS privacy status
@whois.command()
@click.argument("domain")
def retrieve_privacy_status(domain):
    """Retrieve WHOIS privacy status"""
    data = {"domain": domain}
    result = make_request("whois/status", data)
    click.echo(result)