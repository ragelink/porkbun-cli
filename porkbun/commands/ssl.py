import click
from porkbun.api import make_request
from porkbun.utils.exceptions import PorkbunAPIError
from porkbun.utils.validation import validate_domain

@click.group()
def ssl():
    """SSL management commands"""
    pass

# Retrieve SSL bundle for a domain
@ssl.command()
@click.argument("domain")
def retrieve_bundle(domain):
    """Retrieve SSL bundle for a domain"""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
    
    try:
        data = {"domain": domain}
        result = make_request("ssl/retrieve", data)
        if result.get("status") == "error":
            click.echo(result)
            ctx = click.get_current_context()
            ctx.exit(1)
        click.echo(result)
        return 0
    except PorkbunAPIError as e:
        click.echo(f"Error: {str(e)}")
        ctx = click.get_current_context()
        ctx.exit(1)

# Generate SSL bundle for a domain
@ssl.command()
@click.argument("domain")
def generate_bundle(domain):
    """Generate and retrieve SSL bundle for a domain"""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
    
    try:
        # Generate the certificate
        data = {"domain": domain}
        result = make_request("ssl/generate", data)
        
        if result.get("status") == "error":
            click.echo(result)
            ctx = click.get_current_context()
            ctx.exit(1)
        
        # Retrieve the generated certificate
        result = make_request("ssl/retrieve", data)
        if result.get("status") == "error":
            click.echo(result)
            ctx = click.get_current_context()
            ctx.exit(1)
            
        click.echo(result)
        return 0
        
    except PorkbunAPIError as e:
        click.echo(f"Error: {str(e)}")
        ctx = click.get_current_context()
        ctx.exit(1)