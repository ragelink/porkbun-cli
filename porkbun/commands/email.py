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
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        result = asyncio.run(make_request(f"email/retrieve/{domain}", {}))
        if result.get('status') == 'SUCCESS':
            forwards = result.get('forwards', [])
            
            if not forwards:
                console.print(f"[bold yellow]No email forwards found for[/] [bold green]{domain}[/]")
                return 0
                
            table = Table(title=f"Email Forwards for [bold]{domain}[/]", title_style="bold blue", header_style="bold")
            table.add_column("ID", style="dim")
            table.add_column("Email", style="cyan")
            table.add_column("Forward To", style="green")
            table.add_column("Status", style="yellow")
            
            for forward in forwards:
                table.add_row(
                    str(forward.get('id', '')),
                    forward.get('email', ''),
                    forward.get('forward_to', ''),
                    forward.get('status', '')
                )
            
            console.print(table)
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
        return 0
    except PorkbunAPIError as e:
        console.print(f"[error]Error: {str(e)}[/]")
        if "domain is not opted in to api access" in str(e).lower():
            console.print("[info]This error occurs when a domain is not enabled for API access in your Porkbun account.[/]")
            console.print("[info]To fix this issue:[/]")
            console.print("[info]1. Log in to your Porkbun dashboard at https://porkbun.com/account/login[/]")
            console.print("[info]2. Navigate to the domain management page for " + domain + "[/]")
            console.print("[info]3. Look for the 'API Access' option and enable it[/]")
            console.print("[info]4. Try this command again after enabling API access[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)

@email.command()
@click.argument("domain")
@click.argument("email_prefix")
@click.argument("forward_to")
def create_forward(domain, email_prefix, forward_to):
    """Create an email forward
    
    EMAIL_PREFIX: Local part of the email (before @)
    FORWARD_TO: Email address to forward to
    """
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    if not validate_email(forward_to):
        raise click.BadParameter("Invalid forwarding email address")
    
    # Construct the email from prefix and domain
    email = f"{email_prefix}@{domain}"
    
    try:
        result = asyncio.run(make_request("email/create", {
            "domain": domain,
            "email": email,
            "forward_to": forward_to
        }))
        
        if result.get('status') == 'SUCCESS':
            console.print(f"[green]Successfully created email forward:[/]")
            console.print(f"[green]From:[/] {email} → [green]To:[/] {forward_to}")
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
        return 0
    except PorkbunAPIError as e:
        console.print(f"[error]Error: {str(e)}[/]")
        if "domain is not opted in to api access" in str(e).lower():
            console.print("[info]This error occurs when a domain is not enabled for API access in your Porkbun account.[/]")
            console.print("[info]To fix this issue:[/]")
            console.print("[info]1. Log in to your Porkbun dashboard at https://porkbun.com/account/login[/]")
            console.print("[info]2. Navigate to the domain management page for " + domain + "[/]")
            console.print("[info]3. Look for the 'API Access' option and enable it[/]")
            console.print("[info]4. Try this command again after enabling API access[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)

@email.command()
@click.argument("domain")
@click.argument("email_id")
def delete_forward(domain, email_id):
    """Delete an email forward
    
    EMAIL_ID: ID of the email forward to delete
    """
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
    
    try:
        result = asyncio.run(make_request("email/delete", {
            "domain": domain,
            "id": email_id
        }))
        
        if result.get('status') == 'SUCCESS':
            console.print(f"[green]Successfully deleted email forward with ID: {email_id}[/]")
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
        return 0
    except PorkbunAPIError as e:
        console.print(f"[error]Error: {str(e)}[/]")
        if "domain is not opted in to api access" in str(e).lower():
            console.print("[info]This error occurs when a domain is not enabled for API access in your Porkbun account.[/]")
            console.print("[info]To fix this issue:[/]")
            console.print("[info]1. Log in to your Porkbun dashboard at https://porkbun.com/account/login[/]")
            console.print("[info]2. Navigate to the domain management page for " + domain + "[/]")
            console.print("[info]3. Look for the 'API Access' option and enable it[/]")
            console.print("[info]4. Try this command again after enabling API access[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)

@email.command()
@click.argument("domain")
@click.argument("email_id")
@click.argument("forward_to")
def update_forward(domain, email_id, forward_to):
    """Update an email forward's destination
    
    EMAIL_ID: ID of the email forward to update
    FORWARD_TO: New email address to forward to
    """
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    if not validate_email(forward_to):
        raise click.BadParameter("Invalid forwarding email address")
    
    try:
        # First, retrieve the current forward details to get the email
        list_result = asyncio.run(make_request(f"email/retrieve/{domain}", {}))
        if list_result.get('status') != 'SUCCESS':
            console.print(f"[error]Error retrieving forwards: {list_result.get('message', 'Unknown error')}[/]")
            ctx = click.get_current_context()
            ctx.exit(1)
            
        forwards = list_result.get('forwards', [])
        target_forward = next((f for f in forwards if str(f.get('id', '')) == email_id), None)
        
        if not target_forward:
            console.print(f"[error]Error: Email forward with ID {email_id} not found[/]")
            ctx = click.get_current_context()
            ctx.exit(1)
        
        email = target_forward.get('email', '')
        
        # Now update the forward
        result = asyncio.run(make_request("email/update", {
            "domain": domain,
            "id": email_id,
            "email": email,
            "forward_to": forward_to
        }))
        
        if result.get('status') == 'SUCCESS':
            console.print(f"[green]Successfully updated email forward:[/]")
            console.print(f"[green]From:[/] {email} → [green]To:[/] {forward_to}")
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
        return 0
    except PorkbunAPIError as e:
        console.print(f"[error]Error: {str(e)}[/]")
        if "domain is not opted in to api access" in str(e).lower():
            console.print("[info]This error occurs when a domain is not enabled for API access in your Porkbun account.[/]")
            console.print("[info]To fix this issue:[/]")
            console.print("[info]1. Log in to your Porkbun dashboard at https://porkbun.com/account/login[/]")
            console.print("[info]2. Navigate to the domain management page for " + domain + "[/]")
            console.print("[info]3. Look for the 'API Access' option and enable it[/]")
            console.print("[info]4. Try this command again after enabling API access[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)

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
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        # Read batch file
        with open(batch_file, 'r') as f:
            forwards = json.load(f)
            
        if not isinstance(forwards, list):
            console.print("[error]Batch file must contain a JSON array of forwarding objects[/]")
            ctx = click.get_current_context()
            ctx.exit(1)
            
        # Process each forward
        success_count = 0
        error_count = 0
        
        with console.status(f"[bold green]Processing {len(forwards)} email forwards for {domain}...[/]") as status:
            for i, forward in enumerate(forwards):
                email_prefix = forward.get('email_prefix', '')
                forward_to = forward.get('forward_to', '')
                
                # Validate forward
                if not email_prefix or not forward_to:
                    console.print(f"[error]Forward {i+1}: Missing required fields (email_prefix, forward_to)[/]")
                    error_count += 1
                    continue
                    
                if not validate_email(forward_to):
                    console.print(f"[error]Forward {i+1}: Invalid forwarding email address[/]")
                    error_count += 1
                    continue
                
                email = f"{email_prefix}@{domain}"
                status.update(f"[bold green]Processing forward {i+1}/{len(forwards)}: {email} → {forward_to}[/]")
                
                try:
                    result = asyncio.run(make_request("email/create", {
                        "domain": domain,
                        "email": email,
                        "forward_to": forward_to
                    }))
                    
                    if result.get('status') == 'SUCCESS':
                        console.print(f"[green]Created forward: {email} → {forward_to}[/]")
                        success_count += 1
                    else:
                        console.print(f"[error]Failed to create forward {email}: {result.get('message', 'Unknown error')}[/]")
                        error_count += 1
                except Exception as e:
                    console.print(f"[error]Error creating forward {email}: {str(e)}[/]")
                    error_count += 1
        
        # Summary
        if success_count > 0 and error_count == 0:
            console.print(f"[bold green]Successfully created all {success_count} email forwards for {domain}[/]")
        elif success_count > 0:
            console.print(f"[bold yellow]Created {success_count} forwards successfully with {error_count} errors for {domain}[/]")
        else:
            console.print(f"[bold red]Failed to create any email forwards for {domain}[/]")
            
        return 0
    except json.JSONDecodeError:
        console.print(f"[error]Invalid JSON in batch file {batch_file}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)

@email.command()
@click.argument("domain")
@click.argument("email_ids", nargs=-1)
def batch_delete(domain, email_ids):
    """Delete multiple email forwards at once
    
    EMAIL_IDS: One or more email forward IDs to delete
    """
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    if not email_ids:
        console.print("[error]No email IDs provided. Please specify at least one ID to delete.[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
        
    success_count = 0
    error_count = 0
    
    with console.status(f"[bold green]Deleting {len(email_ids)} email forwards from {domain}...[/]") as status:
        for i, email_id in enumerate(email_ids):
            status.update(f"[bold green]Deleting forward {i+1}/{len(email_ids)}: ID {email_id}[/]")
            
            try:
                result = asyncio.run(make_request("email/delete", {
                    "domain": domain,
                    "id": email_id
                }))
                
                if result.get('status') == 'SUCCESS':
                    console.print(f"[green]Successfully deleted email forward ID: {email_id}[/]")
                    success_count += 1
                else:
                    console.print(f"[error]Failed to delete forward {email_id}: {result.get('message', 'Unknown error')}[/]")
                    error_count += 1
            except Exception as e:
                console.print(f"[error]Error deleting forward {email_id}: {str(e)}[/]")
                error_count += 1
    
    # Summary
    if success_count > 0 and error_count == 0:
        console.print(f"[bold green]Successfully deleted all {success_count} email forwards from {domain}[/]")
    elif success_count > 0:
        console.print(f"[bold yellow]Deleted {success_count} forwards successfully with {error_count} errors from {domain}[/]")
    else:
        console.print(f"[bold red]Failed to delete any email forwards from {domain}[/]")
        
    return 0
