import click
from porkbun.api import make_request

@click.group()
def email():
    """Email forwarding commands"""
    pass

# Create an email forward
@email.command()
@click.argument("domain")
@click.argument("email")
@click.argument("forward_to")
def create_forward(domain, email, forward_to):
    """Create an email forward"""
    data = {"domain": domain, "email": email, "forward_to": forward_to}
    result = make_request("email/create", data)
    click.echo(result)

# Retrieve email forwards
@email.command()
@click.argument("domain")
def retrieve_forwards(domain):
    """Retrieve email forwards"""
    data = {"domain": domain}
    result = make_request("email/retrieve", data)
    click.echo(result)

# Update an email forward
@email.command()
@click.argument("domain")
@click.argument("email_id")
@click.argument("email")
@click.argument("forward_to")
def update_forward(domain, email_id, email, forward_to):
    """Update an email forward"""
    data = {"domain": domain, "id": email_id, "email": email, "forward_to": forward_to}
    result = make_request("email/update", data)
    click.echo(result)

# Delete an email forward
@email.command()
@click.argument("domain")
@click.argument("email_id")
def delete_forward(domain, email_id):
    """Delete an email forward"""
    data = {"domain": domain, "id": email_id}
    result = make_request("email/delete", data)
    click.echo(result)
