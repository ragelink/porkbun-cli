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

@domains.group()
def register():
    """Domain registration commands"""
    pass

@domains.group()
def transfer():
    """Domain transfer commands"""
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

def save_to_watch_list(domain: str, target_price: float) -> None:
    """Save a domain to the watch list for price monitoring."""
    watch_list_file = Path.home() / '.porkbun' / 'watchlist.json'
    watch_list_file.parent.mkdir(parents=True, exist_ok=True)
    
    watch_list = {}
    if watch_list_file.exists():
        with open(watch_list_file) as f:
            watch_list = json.load(f)
    
    watch_list[domain] = {
        'target_price': target_price,
        'added_at': time.time()
    }
    
    with open(watch_list_file, 'w') as f:
        json.dump(watch_list, f, indent=2)

def compare_tld_prices(base_domain: str, tld_pricing: Dict) -> List[Dict]:
    """Compare prices across different TLDs for the same domain name."""
    comparisons = []
    name = base_domain.split('.')[0]
    
    for tld, pricing in tld_pricing.items():
        if isinstance(pricing, dict) and 'registration' in pricing:
            domain = f"{name}.{tld}"
            comparisons.append({
                'domain': domain,
                'tld': tld,
                'price': pricing['registration'],
                'renewal': pricing.get('renewal', 'N/A')
            })
    
    return sorted(comparisons, key=lambda x: float(x['price']) if isinstance(x['price'], (int, float, str)) else float('inf'))

def print_price_comparison(comparisons: List[Dict]) -> None:
    """Print price comparison table."""
    if not comparisons:
        return

    table = Table(title="TLD Price Comparison")
    table.add_column("Domain", style="cyan")
    table.add_column("TLD", style="blue")
    table.add_column("Registration", justify="right")
    table.add_column("Renewal", justify="right")

    for comp in comparisons:
        table.add_row(
            comp['domain'],
            comp['tld'],
            f"${comp['price']}",
            f"${comp['renewal']}" if comp['renewal'] != 'N/A' else 'N/A'
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
@click.option('--compare-tlds', is_flag=True, help='Compare prices across TLDs')
@click.option('--export', type=click.Choice(['json', 'csv']), help='Export results to file')
@click.option('--output', type=click.Path(), help='Output file for export')
@click.option('--watch', type=float, help='Add to watch list with target price')
def check(domains: Optional[tuple], file: Optional[str], delay: float, no_progress: bool,
         suggest: bool, compare_tlds: bool, export: Optional[str], output: Optional[str],
         watch: Optional[float]):
    """Check domain availability and compare prices."""
    # Get domains from either command line arguments or file
    domain_list = list(domains) if domains else load_domains_from_file(file)
    if not domain_list:
        console.print("[error]Error: No domains specified[/]")
        raise click.Abort()

    # Get TLD pricing if needed for suggestions or comparison
    tld_pricing = get_tld_pricing() if (suggest or compare_tlds) else {}

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

                # Add to watch list if requested and available
                if watch is not None and result['success'] and result['available']:
                    save_to_watch_list(domain, watch)
                    console.print(f"[info]Added {domain} to watch list with target price ${watch}[/]")

                # Get suggestions for unavailable domains
                if suggest and result['success'] and not result['available']:
                    suggestions = suggest_domains(domain, tld_pricing)
                    if suggestions:
                        all_suggestions.extend(suggestions)
                        print_suggestions(suggestions)

                # Compare TLD prices
                if compare_tlds and result['success']:
                    comparisons = compare_tld_prices(domain, tld_pricing)
                    if comparisons:
                        print_price_comparison(comparisons)

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

    # Print final summary
    print_check_summary(results, tld_pricing)

    # Export results if requested
    if export and output:
        export_results(results, export, output)
        console.print(f"\n[success]Results exported to {output}[/]")

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
@click.option('--years', type=int, default=1, help='Number of years to register for')
@click.option('--nameservers', multiple=True, help='Custom nameservers')
@click.option('--whois-privacy', is_flag=True, help='Enable WHOIS privacy')
@click.option('--force', is_flag=True, help='Skip confirmation')
def bulk(domains: tuple, file: Optional[str], years: int, nameservers: tuple,
         whois_privacy: bool, force: bool):
    """Register multiple domains."""
    domain_list = list(domains) if domains else load_domains_from_file(file)
    if not domain_list:
        console.print("[error]Error: No domains specified[/]")
        raise click.Abort()

    # Validate and check availability first
    available_domains = []
    total_cost = 0.0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Checking domains...", total=len(domain_list))
        
        for domain in domain_list:
            progress.update(task, description=f"Checking {domain}")
            try:
                data = make_request(f"domain/checkDomain/{domain}", {})
                if data.get('status') == 'SUCCESS':
                    if data.get('response', {}).get('avail') == 'yes':
                        price = float(data.get('response', {}).get('price', 0))
                        available_domains.append((domain, price))
                        total_cost += price * years
                    else:
                        console.print(f"[warning]{domain} is not available[/]")
                else:
                    console.print(f"[error]Error checking {domain}: {data.get('message')}[/]")
            except Exception as e:
                console.print(f"[error]Error checking {domain}: {str(e)}[/]")
            progress.advance(task)
            time.sleep(10)  # Rate limit compliance

    if not available_domains:
        console.print("[error]No domains available for registration[/]")
        return

    # Show summary and confirm
    table = Table(title="Domains to Register")
    table.add_column("Domain", style="cyan")
    table.add_column("Price/Year", justify="right")
    table.add_column("Total", justify="right")

    for domain, price in available_domains:
        table.add_row(
            domain,
            f"${price:.2f}",
            f"${price * years:.2f}"
        )

    console.print(table)
    console.print(f"\nTotal cost for {years} year(s): [green]${total_cost:.2f}[/]")
    
    if nameservers:
        console.print("\nCustom nameservers:")
        for ns in nameservers:
            console.print(f"  • {ns}")
    
    if whois_privacy:
        console.print("\n[info]WHOIS privacy will be enabled[/]")

    if not force and not click.confirm("\nDo you want to proceed with registration?"):
        return

    # Register domains
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Registering domains...", total=len(available_domains))
        
        for domain, _ in available_domains:
            progress.update(task, description=f"Registering {domain}")
            try:
                data = {
                    "years": years,
                    "whoisPrivacy": whois_privacy
                }
                if nameservers:
                    data["ns"] = list(nameservers)
                
                result = make_request(f"domain/register/{domain}", data)
                if result.get('status') == 'SUCCESS':
                    console.print(f"[success]Successfully registered {domain}[/]")
                else:
                    console.print(f"[error]Failed to register {domain}: {result.get('message')}[/]")
            except Exception as e:
                console.print(f"[error]Error registering {domain}: {str(e)}[/]")
            progress.advance(task)
            time.sleep(10)  # Rate limit compliance

@transfer.command()
@click.argument('domains', nargs=-1)
@click.option('--file', '-f', type=click.Path(exists=True), help='File containing domains')
@click.option('--auth-code', required=True, help='Authorization code for transfer')
@click.option('--whois-privacy', is_flag=True, help='Enable WHOIS privacy after transfer')
@click.option('--force', is_flag=True, help='Skip confirmation')
def bulk(domains: tuple, file: Optional[str], auth_code: str,
         whois_privacy: bool, force: bool):
    """Transfer multiple domains to Porkbun."""
    domain_list = list(domains) if domains else load_domains_from_file(file)
    if not domain_list:
        console.print("[error]Error: No domains specified[/]")
        raise click.Abort()

    # Check transfer eligibility
    eligible_domains = []
    total_cost = 0.0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Checking transfer eligibility...", total=len(domain_list))
        
        for domain in domain_list:
            progress.update(task, description=f"Checking {domain}")
            try:
                data = make_request(f"domain/transferCheck/{domain}", {})
                if data.get('status') == 'SUCCESS':
                    price = float(data.get('response', {}).get('price', 0))
                    eligible_domains.append((domain, price))
                    total_cost += price
                else:
                    console.print(f"[error]{domain} is not eligible for transfer: {data.get('message')}[/]")
            except Exception as e:
                console.print(f"[error]Error checking {domain}: {str(e)}[/]")
            progress.advance(task)
            time.sleep(10)  # Rate limit compliance

    if not eligible_domains:
        console.print("[error]No domains eligible for transfer[/]")
        return

    # Show summary and confirm
    table = Table(title="Domains to Transfer")
    table.add_column("Domain", style="cyan")
    table.add_column("Transfer Cost", justify="right")

    for domain, price in eligible_domains:
        table.add_row(domain, f"${price:.2f}")

    console.print(table)
    console.print(f"\nTotal transfer cost: [green]${total_cost:.2f}[/]")
    
    if whois_privacy:
        console.print("\n[info]WHOIS privacy will be enabled after transfer[/]")

    if not force and not click.confirm("\nDo you want to proceed with transfer?"):
        return

    # Initiate transfers
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Initiating transfers...", total=len(eligible_domains))
        
        for domain, _ in eligible_domains:
            progress.update(task, description=f"Transferring {domain}")
            try:
                data = {
                    "auth": auth_code,
                    "whoisPrivacy": whois_privacy
                }
                
                result = make_request(f"domain/transfer/{domain}", data)
                if result.get('status') == 'SUCCESS':
                    console.print(f"[success]Successfully initiated transfer for {domain}[/]")
                else:
                    console.print(f"[error]Failed to initiate transfer for {domain}: {result.get('message')}[/]")
            except Exception as e:
                console.print(f"[error]Error transferring {domain}: {str(e)}[/]")
            progress.advance(task)
            time.sleep(10)  # Rate limit compliance

@transfer.command()
def status():
    """Check status of pending transfers."""
    try:
        result = make_request("domain/transferList", {})
        if not result.get('transfers'):
            console.print("[info]No pending transfers[/]")
            return

        table = Table(title="Pending Transfers")
        table.add_column("Domain", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Started", style="dim")
        table.add_column("Updated", style="dim")

        for transfer in result['transfers']:
            table.add_row(
                transfer['domain'],
                transfer['status'],
                transfer.get('startDate', 'N/A'),
                transfer.get('updateDate', 'N/A')
            )

        console.print(table)
    except Exception as e:
        console.print(f"[error]Error checking transfer status: {str(e)}[/]")

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

@domains.command()
def watch_list():
    """Show domains in the watch list."""
    watch_list_file = Path.home() / '.porkbun' / 'watchlist.json'
    if not watch_list_file.exists():
        console.print("[warning]Watch list is empty[/]")
        return

    with open(watch_list_file) as f:
        watch_list = json.load(f)

    if not watch_list:
        console.print("[warning]Watch list is empty[/]")
        return

    table = Table(title="Domain Watch List")
    table.add_column("Domain", style="cyan")
    table.add_column("Target Price", justify="right")
    table.add_column("Current Price", justify="right")
    table.add_column("Status", style="bold")

    for domain, info in watch_list.items():
        try:
            data = make_request(f"domain/checkDomain/{domain}", {})
            current_price = data.get('response', {}).get('price', 'N/A')
            available = data.get('response', {}).get('avail') == 'yes'
            
            status = "[green]Available[/]" if available else "[red]Taken[/]"
            if available and float(current_price) <= info['target_price']:
                status = "[green bold]Target Price Met![/]"
            
            table.add_row(
                domain,
                f"${info['target_price']}",
                f"${current_price}" if current_price != 'N/A' else 'N/A',
                status
            )
            time.sleep(10)  # Rate limit compliance
            
        except Exception as e:
            table.add_row(
                domain,
                f"${info['target_price']}",
                'Error',
                f"[red]{str(e)}[/]"
            )

    console.print(table)