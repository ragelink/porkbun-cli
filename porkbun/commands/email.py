import click
import json
import asyncio
from porkbun.api import make_request
from porkbun.utils.exceptions import PorkbunAPIError
from porkbun.utils.validation import validate_domain, validate_email
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def email():
    """Email forwarding management commands"""
    pass

@email.command()
@click.argument("domain")
def list_forwards(domain):
    """List email forwards for a domain"""
    raise click.ClickException("Not supported: Porkbun's API (v3) has no email retrieve endpoint; manage email forwarding/hosting in the dashboard: https://porkbun.com/account/email")

@email.command()
@click.argument("domain")
@click.argument("email_prefix")
@click.argument("forward_to")
def create_forward(domain, email_prefix, forward_to):
    """Create an email forward

    EMAIL_PREFIX: Local part of the email (before @)
    FORWARD_TO: Email address to forward to
    """
    raise click.ClickException("Not supported: Porkbun's API (v3) has no email create endpoint; manage email forwarding/hosting in the dashboard: https://porkbun.com/account/email")

@email.command()
@click.argument("domain")
@click.argument("email_id")
def delete_forward(domain, email_id):
    """Delete an email forward

    EMAIL_ID: ID of the email forward to delete
    """
    raise click.ClickException("Not supported: Porkbun's API (v3) has no email delete endpoint; manage email forwarding/hosting in the dashboard: https://porkbun.com/account/email")

@email.command()
@click.argument("domain")
@click.argument("email_id")
@click.argument("forward_to")
def update_forward(domain, email_id, forward_to):
    """Update an email forward's destination

    EMAIL_ID: ID of the email forward to update
    FORWARD_TO: New email address to forward to
    """
    raise click.ClickException("Not supported: Porkbun's API (v3) has no email update endpoint; manage email forwarding/hosting in the dashboard: https://porkbun.com/account/email")

@email.command()
@click.argument("domain")
@click.argument("batch_file", type=click.Path(exists=True, readable=True))
def batch_create(domain, batch_file):
    """Create multiple email forwards for a domain using a JSON file

    The JSON file should contain an array of forwarding objects with the following fields:
    - email_prefix: Local part of the email (before @)
    - forward_to: Email address to forward to

    Example JSON file:
    [
        {"email_prefix": "info", "forward_to": "contact@example.com"},
        {"email_prefix": "sales", "forward_to": "sales@example.com"}
    ]
    """
    raise click.ClickException("Not supported: Porkbun's API (v3) has no email create endpoint; manage email forwarding/hosting in the dashboard: https://porkbun.com/account/email")

@email.command()
@click.argument("domain")
@click.argument("email_ids", nargs=-1)
def batch_delete(domain, email_ids):
    """Delete multiple email forwards at once

    EMAIL_IDS: One or more email forward IDs to delete
    """
    raise click.ClickException("Not supported: Porkbun's API (v3) has no email delete endpoint; manage email forwarding/hosting in the dashboard: https://porkbun.com/account/email")
