"""Command chaining and workflow automation for Porkbun CLI."""

import click
import asyncio
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from porkbun.utils.exceptions import PorkbunAPIError
from porkbun.utils.validation import validate_domain
from porkbun.commands.dns import create_record
from porkbun.commands.email import batch_create as email_batch_create
from porkbun.commands.url import batch_add as url_batch_add

console = Console()

@click.group()
def workflow():
    """Command chaining and workflow automation"""
    pass

@workflow.command()
@click.argument("domain")
@click.option("--dns-records", type=click.Path(exists=True, readable=True), help="JSON file with DNS records")
@click.option("--email-forwards", type=click.Path(exists=True, readable=True), help="JSON file with email forwards")
@click.option("--url-forwards", type=click.Path(exists=True, readable=True), help="JSON file with URL forwards")
@click.option("--sequential/--parallel", default=True, help="Run tasks sequentially or in parallel")
def setup_domain(domain: str, dns_records: Optional[str], email_forwards: Optional[str], 
                url_forwards: Optional[str], sequential: bool):
    """Set up multiple aspects of a domain in one command.
    
    This command allows you to set up DNS records, email forwards, and URL forwards
    in a single operation. Provide JSON files for each type of configuration you
    want to apply.
    
    Example:
    porkbun workflow setup-domain example.com --dns-records dns.json --email-forwards emails.json --url-forwards urls.json
    """
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    tasks = []
    results = {"success": [], "error": []}
    
    # Prepare tasks
    if dns_records:
        tasks.append(("DNS Records", _setup_dns_records, domain, dns_records))
    
    if email_forwards:
        tasks.append(("Email Forwards", _setup_email_forwards, domain, email_forwards))
    
    if url_forwards:
        tasks.append(("URL Forwards", _setup_url_forwards, domain, url_forwards))
    
    if not tasks:
        console.print("[yellow]No setup tasks specified. Please provide at least one configuration file.[/]")
        return
    
    # Execute tasks
    if sequential:
        _run_tasks_sequential(tasks, results)
    else:
        asyncio.run(_run_tasks_parallel(tasks, results))
    
    # Summary
    _print_results_summary(results)

def _run_tasks_sequential(tasks: List[tuple], results: Dict[str, List[str]]):
    """Run tasks sequentially with progress display."""
    with Progress() as progress:
        task_progress = progress.add_task("[green]Setting up domain...", total=len(tasks))
        
        for name, func, domain, config_file in tasks:
            progress.update(task_progress, description=f"[green]Setting up {name}...")
            try:
                func(domain, config_file)
                results["success"].append(name)
                console.print(f"[green]✓ {name} setup completed successfully[/]")
            except Exception as e:
                results["error"].append(f"{name}: {str(e)}")
                console.print(f"[red]✗ {name} setup failed: {str(e)}[/]")
            progress.update(task_progress, advance=1)

async def _run_tasks_parallel(tasks: List[tuple], results: Dict[str, List[str]]):
    """Run tasks in parallel."""
    console.print("[bold]Running setup tasks in parallel...[/]")
    
    async def run_task(name, func, domain, config_file):
        try:
            # Use run_in_executor for CPU-bound tasks
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, func, domain, config_file)
            results["success"].append(name)
            console.print(f"[green]✓ {name} setup completed successfully[/]")
        except Exception as e:
            results["error"].append(f"{name}: {str(e)}")
            console.print(f"[red]✗ {name} setup failed: {str(e)}[/]")
    
    # Create and run tasks
    coroutines = [run_task(name, func, domain, config_file) 
                 for name, func, domain, config_file in tasks]
    await asyncio.gather(*coroutines)

def _print_results_summary(results: Dict[str, List[str]]):
    """Print a summary of the results."""
    table = Table(title="Domain Setup Results")
    
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    # Add successful tasks
    for task in results["success"]:
        table.add_row(task, "[green]Success[/]")
    
    # Add failed tasks
    for error in results["error"]:
        task, message = error.split(":", 1)
        table.add_row(task, f"[red]Failed[/] - {message}")
    
    console.print(table)

def _setup_dns_records(domain: str, config_file: str):
    """Set up DNS records for a domain."""
    # Read DNS records configuration
    with open(config_file, 'r') as f:
        records = json.load(f)
    
    if not isinstance(records, list):
        raise ValueError("DNS records configuration must be a JSON array")
    
    ctx = click.Context(create_record)
    for record in records:
        if not all(k in record for k in ["type", "name", "content", "ttl"]):
            raise ValueError(f"Invalid DNS record format: {record}")
        
        # Convert to args list for create_record
        args = [domain, record["type"], record["content"], str(record["ttl"])]
        if record.get("name"):
            args.extend(["--name", record["name"]])
        if record.get("priority"):
            args.extend(["--priority", str(record["priority"])])
        
        # Execute create_record command
        result = create_record.callback(*args)
        if result != 0:
            raise ValueError(f"Failed to create DNS record: {record}")

def _setup_email_forwards(domain: str, config_file: str):
    """Set up email forwards for a domain."""
    # Execute email batch-create command
    ctx = click.Context(email_batch_create)
    result = email_batch_create.callback(domain, config_file)
    if result != 0:
        raise ValueError("Failed to set up email forwards")

def _setup_url_forwards(domain: str, config_file: str):
    """Set up URL forwards for a domain."""
    # Execute url batch-add command
    ctx = click.Context(url_batch_add)
    result = url_batch_add.callback(domain, config_file)
    if result != 0:
        raise ValueError("Failed to set up URL forwards")

@workflow.command()
@click.argument("domain")
@click.option("--dns-types", multiple=True, help="DNS record types to include (A, AAAA, CNAME, etc.)")
@click.option("--include-email/--exclude-email", default=True, help="Include email forwards")
@click.option("--include-url/--exclude-url", default=True, help="Include URL forwards")
@click.option("--output-dir", type=click.Path(dir_okay=True, file_okay=False), 
              default=".", help="Directory to save configuration files")
def export_config(domain: str, dns_types: List[str], include_email: bool, 
                 include_url: bool, output_dir: str):
    """Export domain configuration to JSON files.
    
    This command exports the current configuration of a domain to JSON files
    that can be used with the setup-domain command or individually with 
    other commands.
    
    Example:
    porkbun workflow export-config example.com --dns-types A CNAME MX --output-dir ./configs
    """
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
    
    output_path = Path(output_dir)
    if not output_path.exists():
        output_path.mkdir(parents=True)
    
    with console.status(f"[bold green]Exporting configuration for {domain}...[/]") as status:
        success_count = 0
        
        # Export DNS records
        if dns_types:
            try:
                status.update(f"[bold green]Exporting DNS records for {domain}...[/]")
                _export_dns_records(domain, dns_types, output_path)
                success_count += 1
                console.print(f"[green]✓ DNS records exported to {output_path / f'{domain}_dns.json'}[/]")
            except Exception as e:
                console.print(f"[red]✗ Failed to export DNS records: {str(e)}[/]")
        
        # Export email forwards
        if include_email:
            try:
                status.update(f"[bold green]Exporting email forwards for {domain}...[/]")
                _export_email_forwards(domain, output_path)
                success_count += 1
                console.print(f"[green]✓ Email forwards exported to {output_path / f'{domain}_email.json'}[/]")
            except Exception as e:
                console.print(f"[red]✗ Failed to export email forwards: {str(e)}[/]")
        
        # Export URL forwards
        if include_url:
            try:
                status.update(f"[bold green]Exporting URL forwards for {domain}...[/]")
                _export_url_forwards(domain, output_path)
                success_count += 1
                console.print(f"[green]✓ URL forwards exported to {output_path / f'{domain}_url.json'}[/]")
            except Exception as e:
                console.print(f"[red]✗ Failed to export URL forwards: {str(e)}[/]")
    
    # Summary
    if success_count > 0:
        console.print(f"[bold green]Successfully exported {success_count} configuration files for {domain}[/]")
    else:
        console.print(f"[bold red]Failed to export any configuration for {domain}[/]")

def _export_dns_records(domain: str, dns_types: List[str], output_path: Path):
    """Export DNS records for a domain."""
    # This would use the DNS retrieve command and filter by types
    # For now, we'll just create a placeholder
    raise NotImplementedError("DNS record export not yet implemented")

def _export_email_forwards(domain: str, output_path: Path):
    """Export email forwards for a domain."""
    # This would use the email list-forwards command
    # For now, we'll just create a placeholder
    raise NotImplementedError("Email forwards export not yet implemented")

def _export_url_forwards(domain: str, output_path: Path):
    """Export URL forwards for a domain."""
    # This would use the URL list-forwards command
    # For now, we'll just create a placeholder
    raise NotImplementedError("URL forwards export not yet implemented") 