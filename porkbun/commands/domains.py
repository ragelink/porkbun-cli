import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.theme import Theme
from typing import List, Optional, Dict
import time
import json
import csv
from pathlib import Path

from porkbun.api import make_request

# Initialize rich console with custom theme
console = Console(theme=Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green",
}))

@click.group()
def domains():
    """Domain management commands"""
    pass

@domains.group()
def dns():
    """DNS record management commands"""
    pass

@domains.group()
def ssl():
    """SSL certificate management commands"""
    pass

@domains.group()
def account():
    """Account management commands"""
    pass

def load_domains_from_file(file_path: str) -> List[str]:
    """Load domain names from a file, one domain per line."""
    try:
        with open(file_path) as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        console.print(f"[error]Error reading file {file_path}: {e}[/]")
        raise click.Abort()

def export_results(results: List[dict], format: str, output: str) -> None:
    """Export results to a file in the specified format."""
    if format == 'json':
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
    elif format == 'csv':
        with open(output, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['domain', 'available', 'price', 'error'])
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'domain': result['domain'],
                    'available': result['available'],
                    'price': result['price'],
                    'error': result['error']
                })

def get_tld_pricing() -> Dict:
    """Get pricing for all TLDs."""
    try:
        data = make_request("pricing/get", {})
        if data.get('status') == 'SUCCESS':
            return data.get('pricing', {})
    except Exception as e:
        console.print(f"[warning]Could not fetch TLD pricing: {e}[/]")
    return {}

def suggest_domains(base_domain: str, tld_pricing: Dict) -> List[Dict]:
    """Suggest alternative domain names based on available TLDs."""
    suggestions = []
    name = base_domain.split('.')[0]
    
    for tld, pricing in tld_pricing.items():
        if isinstance(pricing, dict):  # Some responses might be malformed
            suggested_domain = f"{name}.{tld}"
            try:
                data = make_request(f"domain/checkDomain/{suggested_domain}", {})
                if data.get('status') == 'SUCCESS' and data.get('response', {}).get('avail') == 'yes':
                    suggestions.append({
                        'domain': suggested_domain,
                        'price': pricing.get('registration', 'N/A'),
                        'available': True
                    })
            except Exception:
                continue
            
            if len(suggestions) >= 5:  # Limit to 5 suggestions
                break
                
    return suggestions

def print_check_result(result: dict) -> None:
    """Print the domain check result in a formatted way."""
    domain = result['domain']
    if result['success']:
        if result['available']:
            console.print(f"[success]✓[/] {domain} is available for registration at [success]${result['price']}[/]/year")
        else:
            console.print(f"[error]✗[/] {domain} is already registered")
    else:
        console.print(f"[warning]![/] Error checking {domain}: [error]{result['error']}[/]")

def print_check_summary(results: List[dict], tld_pricing: Optional[Dict] = None) -> None:
    """Print a summary table of all domain check results."""
    table = Table(title="Domain Check Summary")
    table.add_column("Domain", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Price/Year", justify="right")
    table.add_column("Error", style="red")

    available_count = 0
    total_cost = 0.0

    for result in results:
        status = ""
        price = ""
        error = ""

        if result['success']:
            if result['available']:
                status = "[green]Available[/]"
                price = f"${result['price']}"
                available_count += 1
                try:
                    total_cost += float(result['price'])
                except (TypeError, ValueError):
                    pass
            else:
                status = "[red]Taken[/]"
        else:
            status = "[yellow]Error[/]"
            error = result['error']

        table.add_row(result['domain'], status, price, error)

    console.print(table)
    console.print(f"\nSummary:")
    console.print(f"- Total domains checked: [cyan]{len(results)}[/]")
    console.print(f"- Available domains: [green]{available_count}[/]")
    if available_count > 0:
        console.print(f"- Total cost for all available domains: [green]${total_cost:.2f}[/]/year")

def print_suggestions(suggestions: List[Dict]) -> None:
    """Print domain suggestions in a table."""
    if not suggestions:
        return

    console.print("\n[info]Alternative domain suggestions:[/]")
    table = Table()
    table.add_column("Domain", style="cyan")
    table.add_column("Price/Year", justify="right")

    for suggestion in suggestions:
        table.add_row(
            suggestion['domain'],
            f"${suggestion['price']}"
        )

    console.print(table)

# List all domains
@domains.command()
def list_all():
    """List all domains"""
    result = make_request("domain/listAll", {})
    click.echo(result)

# Check domain availability
@domains.command()
@click.option('-d', '--domains', multiple=True, help='One or more domains to check')
@click.option('-f', '--file', type=click.Path(exists=True), help='File containing domains (one per line)')
@click.option('--delay', type=float, default=10.0, help='Delay between requests in seconds (default: 10.0)')
@click.option('--no-progress', is_flag=True, help='Disable progress bar')
@click.option('--suggest', is_flag=True, help='Suggest alternative domains')
@click.option('--export', type=click.Choice(['json', 'csv']), help='Export results to file')
@click.option('--output', type=click.Path(), help='Output file for export')
def check(domains: Optional[tuple], file: Optional[str], delay: float, no_progress: bool,
         suggest: bool, export: Optional[str], output: Optional[str]):
    """Check domain availability."""
    # Get domains from either command line arguments or file
    domain_list = list(domains) if domains else load_domains_from_file(file)
    if not domain_list:
        console.print("[error]Error: No domains specified[/]")
        raise click.Abort()

    # Get TLD pricing if needed for suggestions
    tld_pricing = get_tld_pricing() if suggest else {}

    results = []
    all_suggestions = []

    # Check each domain with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        disable=no_progress
    ) as progress:
        task = progress.add_task(f"Checking {len(domain_list)} domains...", total=len(domain_list))
        
        for i, domain in enumerate(domain_list, 1):
            progress.update(task, description=f"Checking domain {i}/{len(domain_list)}: {domain}")
            try:
                data = make_request(f"domain/checkDomain/{domain}", {})
                result = {
                    'domain': domain,
                    'success': data.get('status') == 'SUCCESS',
                    'available': data.get('response', {}).get('avail') == 'yes',
                    'price': data.get('response', {}).get('price'),
                    'error': data.get('message') if data.get('status') != 'SUCCESS' else None
                }
                results.append(result)
                print_check_result(result)

                # Get suggestions for unavailable domains
                if suggest and result['success'] and not result['available']:
                    suggestions = suggest_domains(domain, tld_pricing)
                    if suggestions:
                        all_suggestions.extend(suggestions)
                        print_suggestions(suggestions)

            except Exception as e:
                console.print(f"[error]Error checking {domain}: {str(e)}[/]")
                results.append({
                    'domain': domain,
                    'success': False,
                    'available': False,
                    'price': None,
                    'error': str(e)
                })
            
            if i < len(domain_list):
                progress.update(task, description=f"Waiting {delay}s before next request...")
                time.sleep(delay)
            
            progress.advance(task)

    # Print summary table
    console.print("\n")
    print_check_summary(results)

    # Export results if requested
    if export and output:
        try:
            export_results(results, export, output)
            console.print(f"\n[success]Results exported to {output}[/]")
        except Exception as e:
            console.print(f"\n[error]Error exporting results: {e}[/]")

# Create a new domain
@domains.command()
@click.argument("domain")
@click.argument("password")
def create(domain, password):
    """Create a new domain"""
    data = {"domain": domain, "password": password}
    result = make_request("domain/create", data)
    click.echo(result)

# Delete a domain
@domains.command()
@click.argument("domain")
def delete(domain):
    """Delete a domain"""
    data = {"domain": domain}
    result = make_request("domain/delete", data)
    click.echo(result)

# Update name servers for a domain
@domains.command()
@click.argument("domain")
@click.argument("nameservers", nargs=-1)
def update_name_servers(domain, nameservers):
    """Update name servers for a domain"""
    data = {"domain": domain, "nameservers": list(nameservers)}
    result = make_request("domain/updateNameServers", data)
    click.echo(result)

# Retrieve name servers for a domain
@domains.command()
@click.argument("domain")
def retrieve_name_servers(domain):
    """Retrieve name servers for a domain"""
    data = {"domain": domain}
    result = make_request("domain/retrieveNameServers", data)
    click.echo(result)

# List contacts for a domain
@domains.command()
@click.argument("domain")
def list_contacts(domain):
    """List domain contacts"""
    data = {"domain": domain}
    result = make_request("domain/listContacts", data)
    click.echo(result)

# Update contacts for a domain
@domains.command()
@click.argument("domain")
@click.argument("contacts", nargs=-1)
def update_contacts(domain, contacts):
    """Update domain contacts"""
    data = {"domain": domain, "contacts": list(contacts)}
    result = make_request("domain/updateContacts", data)
    click.echo(result)

@dns.command()
@click.argument('domain')
def list_records(domain: str):
    """List all DNS records for a domain"""
    try:
        result = make_request(f"dns/retrieve/{domain}", {})
        if result.get('status') == 'SUCCESS':
            records = result.get('records', [])
            
            table = Table(title=f"DNS Records for {domain}")
            table.add_column("Type", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Content", style="yellow")
            table.add_column("TTL", justify="right")
            table.add_column("ID", style="dim")
            
            for record in records:
                table.add_row(
                    record.get('type', ''),
                    record.get('name', ''),
                    record.get('content', ''),
                    str(record.get('ttl', '')),
                    record.get('id', '')
                )
            
            console.print(table)
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")

@dns.command()
@click.argument('domain')
@click.option('--type', '-t', required=True, help='Record type (A, AAAA, CNAME, etc.)')
@click.option('--name', '-n', required=True, help='Record name')
@click.option('--content', '-c', required=True, help='Record content')
@click.option('--ttl', default=600, help='Time to live (default: 600)')
def create_record(domain: str, type: str, name: str, content: str, ttl: int):
    """Create a new DNS record"""
    data = {
        "name": name,
        "type": type.upper(),
        "content": content,
        "ttl": ttl
    }
    
    try:
        result = make_request(f"dns/create/{domain}", data)
        if result.get('status') == 'SUCCESS':
            console.print(f"[success]Successfully created {type} record for {name}[/]")
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")

@dns.command()
@click.argument('domain')
@click.argument('record_id')
def delete_record(domain: str, record_id: str):
    """Delete a DNS record"""
    try:
        result = make_request(f"dns/delete/{domain}/{record_id}", {})
        if result.get('status') == 'SUCCESS':
            console.print(f"[success]Successfully deleted record {record_id}[/]")
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")

@dns.command()
@click.argument('domain')
@click.argument('record_id')
@click.option('--type', '-t', help='Record type (A, AAAA, CNAME, etc.)')
@click.option('--name', '-n', help='Record name')
@click.option('--content', '-c', help='Record content')
@click.option('--ttl', type=int, help='Time to live')
def edit_record(domain: str, record_id: str, type: Optional[str], name: Optional[str],
                content: Optional[str], ttl: Optional[int]):
    """Edit a DNS record"""
    # First get the existing record
    try:
        current = make_request(f"dns/retrieve/{domain}", {})
        if current.get('status') != 'SUCCESS':
            console.print(f"[error]Error retrieving current record: {current.get('message', 'Unknown error')}[/]")
            return
            
        record = next((r for r in current.get('records', []) if r.get('id') == record_id), None)
        if not record:
            console.print(f"[error]Record {record_id} not found[/]")
            return
            
        # Update with new values, keeping old ones if not specified
        data = {
            "name": name if name is not None else record.get('name', ''),
            "type": type.upper() if type is not None else record.get('type', ''),
            "content": content if content is not None else record.get('content', ''),
            "ttl": ttl if ttl is not None else record.get('ttl', 600)
        }
        
        result = make_request(f"dns/edit/{domain}/{record_id}", data)
        if result.get('status') == 'SUCCESS':
            console.print(f"[success]Successfully updated record {record_id}[/]")
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")

@domains.command()
@click.argument('domains', nargs=-1)
@click.option('--file', '-f', type=click.Path(exists=True), help='File containing domains')
@click.option('--years', type=int, default=1, help='Number of years to renew for')
@click.option('--force', is_flag=True, help='Skip confirmation')
def renew(domains: tuple, file: Optional[str], years: int, force: bool):
    """Renew multiple domains"""
    domain_list = list(domains)
    if file:
        domain_list.extend(load_domains_from_file(file))
        
    if not domain_list:
        console.print("[error]No domains specified[/]")
        return
        
    # Get renewal prices
    total_cost = 0
    renewals = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Checking renewal prices...", total=len(domain_list))
        
        for domain in domain_list:
            try:
                result = make_request(f"domain/getRenewalPrice/{domain}", {})
                if result.get('status') == 'SUCCESS':
                    price = float(result.get('renewalPrice', 0))
                    total_cost += price * years
                    renewals.append({
                        'domain': domain,
                        'price': price,
                        'years': years
                    })
                else:
                    console.print(f"[error]Error getting price for {domain}: {result.get('message')}[/]")
            except Exception as e:
                console.print(f"[error]Error checking {domain}: {str(e)}[/]")
            progress.advance(task)
    
    if not renewals:
        console.print("[error]No valid domains to renew[/]")
        return
        
    # Show renewal summary
    table = Table(title="Renewal Summary")
    table.add_column("Domain", style="cyan")
    table.add_column("Years", justify="right")
    table.add_column("Price/Year", justify="right")
    table.add_column("Total", justify="right", style="bold")
    
    for renewal in renewals:
        table.add_row(
            renewal['domain'],
            str(renewal['years']),
            f"${renewal['price']:.2f}",
            f"${renewal['price'] * renewal['years']:.2f}"
        )
    
    console.print(table)
    console.print(f"\nTotal cost: [bold green]${total_cost:.2f}[/]")
    
    if not force and not click.confirm("Do you want to proceed with the renewal?"):
        return
        
    # Process renewals
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Processing renewals...", total=len(renewals))
        
        for renewal in renewals:
            try:
                result = make_request("domain/renew", {
                    "domain": renewal['domain'],
                    "years": renewal['years']
                })
                if result.get('status') == 'SUCCESS':
                    console.print(f"[success]Successfully renewed {renewal['domain']} for {renewal['years']} years[/]")
                else:
                    console.print(f"[error]Error renewing {renewal['domain']}: {result.get('message')}[/]")
            except Exception as e:
                console.print(f"[error]Error renewing {renewal['domain']}: {str(e)}[/]")
            progress.advance(task)

@ssl.command()
@click.argument('domain')
def retrieve(domain: str):
    """Retrieve SSL certificate details"""
    try:
        result = make_request(f"ssl/retrieve/{domain}", {})
        if result.get('status') == 'SUCCESS':
            cert_data = result.get('certificateDetails', {})
            
            # Create a rich table for certificate details
            table = Table(title=f"SSL Certificate Details for {domain}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            # Add certificate details to table
            table.add_row("Status", cert_data.get('status', 'Unknown'))
            table.add_row("Type", cert_data.get('type', 'Unknown'))
            table.add_row("Expires", cert_data.get('expires', 'Unknown'))
            
            console.print(table)
            
            # Show the certificate chain
            if 'chain' in cert_data:
                console.print("\n[bold]Certificate Chain:[/]")
                for cert in cert_data['chain']:
                    console.print(f"[dim]{cert}[/]")
            
            # Show installation instructions if available
            if 'installationInstructions' in cert_data:
                console.print("\n[bold]Installation Instructions:[/]")
                console.print(cert_data['installationInstructions'])
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")

@ssl.command()
@click.argument('domain')
def generate(domain: str):
    """Generate a new SSL certificate"""
    try:
        result = make_request(f"ssl/generate/{domain}", {})
        if result.get('status') == 'SUCCESS':
            console.print(f"[success]Successfully generated SSL certificate for {domain}[/]")
            # Show the certificate details
            retrieve.callback(domain)
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")

@account.command()
def balance():
    """Check account balance"""
    try:
        result = make_request("balance", {})
        if result.get('status') == 'SUCCESS':
            balance = result.get('balance', 0)
            console.print(f"Current balance: [green]${balance:.2f}[/]")
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")

@account.command()
@click.option('--limit', type=int, default=10, help='Number of transactions to show')
def transactions(limit: int):
    """View recent transactions"""
    try:
        result = make_request("transactions", {"limit": limit})
        if result.get('status') == 'SUCCESS':
            transactions = result.get('transactions', [])
            
            table = Table(title="Recent Transactions")
            table.add_column("Date", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Description")
            table.add_column("Amount", justify="right", style="green")
            table.add_column("Balance", justify="right")
            
            for tx in transactions:
                amount = float(tx.get('amount', 0))
                amount_str = f"${abs(amount):.2f}"
                if amount < 0:
                    amount_str = f"-{amount_str}"
                
                table.add_row(
                    tx.get('date', ''),
                    tx.get('type', ''),
                    tx.get('description', ''),
                    amount_str,
                    f"${float(tx.get('balance', 0)):.2f}"
                )
            
            console.print(table)
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")

@domains.command()
@click.argument('domain')
def whois(domain: str):
    """Get WHOIS information for a domain"""
    try:
        result = make_request(f"whois/{domain}", {})
        if result.get('status') == 'SUCCESS':
            whois_data = result.get('whois', {})
            
            table = Table(title=f"WHOIS Information for {domain}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            # Add WHOIS details to table
            for key, value in whois_data.items():
                if isinstance(value, (list, tuple)):
                    value = '\n'.join(value)
                elif isinstance(value, dict):
                    value = '\n'.join(f"{k}: {v}" for k, v in value.items())
                table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(table)
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")

@domains.command()
@click.argument('domain')
@click.option('--enable/--disable', default=True, help='Enable or disable WHOIS privacy')
def privacy(domain: str, enable: bool):
    """Manage WHOIS privacy for a domain"""
    try:
        endpoint = "enableWhoisPrivacy" if enable else "disableWhoisPrivacy"
        result = make_request(f"domain/{endpoint}/{domain}", {})
        if result.get('status') == 'SUCCESS':
            status = "enabled" if enable else "disabled"
            console.print(f"[success]Successfully {status} WHOIS privacy for {domain}[/]")
        else:
            console.print(f"[error]Error: {result.get('message', 'Unknown error')}[/]")
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/]")