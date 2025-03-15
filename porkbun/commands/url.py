import click
import json
import asyncio
from porkbun.api import make_request
from porkbun.utils.exceptions import PorkbunAPIError
from porkbun.utils.validation import validate_domain
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def url():
    """URL forwarding management commands"""
    pass

@url.command()
@click.argument("domain")
def list_forwards(domain):
    """List URL forwards for a domain"""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        result = asyncio.run(make_request(f"domain/getUrlForwarding/{domain}", {}))
        if result.get('status') == 'SUCCESS':
            forwards = result.get('forwards', [])
            
            if not forwards:
                console.print(f"[bold yellow]No URL forwards found for[/] [bold green]{domain}[/]")
                return 0
                
            table = Table(title=f"URL Forwards for [bold]{domain}[/]", title_style="bold blue", header_style="bold")
            table.add_column("Source", style="cyan")
            table.add_column("Destination", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Title", style="magenta")
            
            for forward in forwards:
                table.add_row(
                    forward.get('source', ''),
                    forward.get('destination', ''),
                    forward.get('type', ''),
                    forward.get('title', '')
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

@url.command()
@click.argument("domain")
@click.argument("source")
@click.argument("destination")
@click.option("--type", type=click.Choice(["301", "302", "iframe"]), default="301", help="Redirect type: 301 (permanent), 302 (temporary), or iframe")
@click.option("--title", help="Title for iframe redirects")
def add_forward(domain, source, destination, type, title):
    """Add URL forward for a domain
    
    SOURCE: Source path (e.g., 'blog' or '/' for root)
    DESTINATION: Destination URL (e.g., 'https://example.com/blog')
    """
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    # Normalize source path
    if source == '/' or source == '':
        source = ''
    elif source.startswith('/'):
        source = source[1:]
    
    # Build request data
    data = {
        "source": source,
        "destination": destination,
        "type": type
    }
    
    # Add title for iframe redirects
    if type == "iframe" and title:
        data["title"] = title
    
    try:
        result = asyncio.run(make_request(f"domain/addUrlForward/{domain}", data))
        if result.get('status') == 'SUCCESS':
            console.print(f"[green]Successfully added URL forward:[/]")
            console.print(f"[green]Source:[/] {source or '/'} → [green]Destination:[/] {destination} ([green]Type:[/] {type})")
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

@url.command()
@click.argument("domain")
@click.argument("source")
def delete_forward(domain, source):
    """Delete URL forward for a domain
    
    SOURCE: Source path to delete (e.g., 'blog' or '/' for root)
    """
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    # Normalize source path
    if source == '/' or source == '':
        source = ''
    elif source.startswith('/'):
        source = source[1:]
    
    try:
        result = asyncio.run(make_request(f"domain/deleteUrlForward/{domain}/{source}", {}))
        if result.get('status') == 'SUCCESS':
            console.print(f"[green]Successfully deleted URL forward for path: {source or '/'}[/]")
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

@url.command()
@click.argument("domain")
@click.argument("batch_file", type=click.Path(exists=True, readable=True))
def batch_add(domain, batch_file):
    """Add multiple URL forwards for a domain using a JSON file
    
    The JSON file should contain an array of forwarding objects with the following fields:
    - source: Source path (e.g., 'blog' or '/' for root)
    - destination: Destination URL (e.g., 'https://example.com/blog')
    - type: Redirect type ('301', '302', or 'iframe') - optional, defaults to '301'
    - title: Title for iframe redirects - optional
    
    Example JSON file:
    [
        {"source": "blog", "destination": "https://example.com/blog", "type": "301"},
        {"source": "shop", "destination": "https://shop.example.com", "type": "302"}
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
        
        with console.status(f"[bold green]Processing {len(forwards)} URL forwards for {domain}...[/]") as status:
            for i, forward in enumerate(forwards):
                source = forward.get('source', '')
                destination = forward.get('destination', '')
                forward_type = forward.get('type', '301')
                title = forward.get('title', '')
                
                # Validate forward
                if not destination:
                    console.print(f"[error]Forward {i+1}: Missing required field 'destination'[/]")
                    error_count += 1
                    continue
                    
                # Normalize source path
                if source == '/' or source == '':
                    source = ''
                elif source.startswith('/'):
                    source = source[1:]
                
                status.update(f"[bold green]Processing forward {i+1}/{len(forwards)}: {source or '/'} → {destination}[/]")
                
                # Build request data
                data = {
                    "source": source,
                    "destination": destination,
                    "type": forward_type
                }
                
                # Add title for iframe redirects
                if forward_type == "iframe" and title:
                    data["title"] = title
                
                try:
                    result = asyncio.run(make_request(f"domain/addUrlForward/{domain}", data))
                    if result.get('status') == 'SUCCESS':
                        console.print(f"[green]Added forward: {source or '/'} → {destination} (Type: {forward_type})[/]")
                        success_count += 1
                    else:
                        console.print(f"[error]Failed to add forward {source or '/'}: {result.get('message', 'Unknown error')}[/]")
                        error_count += 1
                except Exception as e:
                    console.print(f"[error]Error adding forward {source or '/'}: {str(e)}[/]")
                    error_count += 1
        
        # Summary
        if success_count > 0 and error_count == 0:
            console.print(f"[bold green]Successfully added all {success_count} URL forwards for {domain}[/]")
        elif success_count > 0:
            console.print(f"[bold yellow]Added {success_count} forwards successfully with {error_count} errors for {domain}[/]")
        else:
            console.print(f"[bold red]Failed to add any URL forwards for {domain}[/]")
            
        return 0
    except json.JSONDecodeError:
        console.print(f"[error]Invalid JSON in batch file {batch_file}[/]")
        ctx = click.get_current_context()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")
        ctx = click.get_current_context()
        ctx.exit(1) 