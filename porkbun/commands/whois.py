import click

# NOTE: Porkbun's public API (v3) has no WHOIS-privacy endpoints. WHOIS privacy
# is set automatically at registration and managed from the Porkbun dashboard,
# so these commands can only point users there rather than call the API.
_UNSUPPORTED = (
    "Not supported: Porkbun's API (v3) has no WHOIS-privacy endpoint. "
    "WHOIS privacy is enabled by default and managed from the dashboard: "
    "https://porkbun.com/account/domainsSpeedy"
)


@click.group()
def whois():
    """WHOIS privacy commands (not supported by the Porkbun API)"""
    pass


# Enable WHOIS privacy
@whois.command()
@click.argument("domain")
def enable_privacy(domain):
    """Enable WHOIS privacy (unsupported by the Porkbun API)"""
    raise click.ClickException(_UNSUPPORTED)


# Disable WHOIS privacy
@whois.command()
@click.argument("domain")
def disable_privacy(domain):
    """Disable WHOIS privacy (unsupported by the Porkbun API)"""
    raise click.ClickException(_UNSUPPORTED)


# Retrieve WHOIS privacy status
@whois.command()
@click.argument("domain")
def retrieve_privacy_status(domain):
    """Retrieve WHOIS privacy status (unsupported by the Porkbun API)"""
    raise click.ClickException(_UNSUPPORTED)
