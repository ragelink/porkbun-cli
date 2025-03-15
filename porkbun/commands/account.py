import click
import json
import asyncio
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional, Dict, List

from porkbun.api import make_request
from porkbun.utils.validation import validate_domain

console = Console()

@click.group()
def account():
    """Account management commands"""
    pass

@account.command()
def ping():
    """Test API connectivity."""
    try:
        result = asyncio.run(make_request("ping", {}))
        if result.get('status') == 'SUCCESS':
            console.print(f"[success]API connection successful![/]")
            console.print(f"Your IP: {result.get('yourIp', 'Unknown')}")
        else:
            console.print(f"[error]Error connecting to API: {result.get('message')}[/]")
    except Exception as e:
        console.print(f"[error]Error connecting to API: {str(e)}[/]")

@account.command()
def balance():
    """Check account balance."""
    try:
        # Run the async function in an event loop
        result = asyncio.run(make_request("balance/get", {}))
        if result.get('status') == 'SUCCESS':
            table = Table(title="Account Balance")
            table.add_column("Balance", style="green")
            table.add_column("Currency", style="dim")
            
            table.add_row(
                f"${result.get('balance', '0.00')}",
                result.get('currency', 'USD')
            )
            
            console.print(table)
        else:
            console.print(f"[error]Error checking balance: {result.get('message')}[/]")
    except Exception as e:
        console.print(f"[error]Error checking balance: {str(e)}[/]")

@account.command()
@click.option('--limit', type=int, default=10, help='Number of transactions to show')
@click.option('--export', type=click.Choice(['json', 'csv']), help='Export format')
@click.option('--output', type=click.Path(), help='Output file path')
def transactions(limit: int, export: Optional[str], output: Optional[str]):
    """View transaction history."""
    try:
        # Run the async function in an event loop
        result = asyncio.run(make_request("billing/list", {}))
        if result.get('status') == 'SUCCESS':
            transactions = result.get('transactions', [])
            if not transactions:
                console.print("[info]No transactions found[/]")
                return
                
            # Sort transactions by date
            transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # Limit the number of transactions
            transactions = transactions[:limit]
            
            if export:
                export_transactions(transactions, export, output)
            else:
                table = Table(title="Transaction History")
                table.add_column("Date", style="dim")
                table.add_column("Description")
                table.add_column("Amount", justify="right", style="bold")
                table.add_column("Type", style="cyan")
                
                for tx in transactions:
                    amount = float(tx.get('amount', 0))
                    amount_str = f"${abs(amount):.2f}"
                    tx_type = "[green]Credit[/]" if amount > 0 else "[red]Debit[/]"
                    
                    table.add_row(
                        tx.get('date', 'N/A'),
                        tx.get('description', 'N/A'),
                        amount_str,
                        tx_type
                    )
                
                console.print(table)
        else:
            console.print(f"[error]Error retrieving transactions: {result.get('message')}[/]")
    except Exception as e:
        console.print(f"[error]Error retrieving transactions: {str(e)}[/]")

@account.group()
def portfolio():
    """Domain portfolio management"""
    pass

@portfolio.command()
@click.option('--group', help='Filter by group')
@click.option('--tag', help='Filter by tag')
@click.option('--export', type=click.Choice(['json', 'csv']), help='Export format')
@click.option('--output', type=click.Path(), help='Output file path')
def list_domains(group: Optional[str], tag: Optional[str], export: Optional[str], output: Optional[str]):
    """List domains in portfolio."""
    try:
        result = make_request("domain/listAll", {})
        if result.get('status') == 'SUCCESS':
            domains = result.get('domains', [])
            if not domains:
                console.print("[info]No domains found[/]")
                return
                
            # Load domain metadata
            metadata = load_domain_metadata()
            
            # Filter domains by group/tag
            if group or tag:
                domains = [
                    d for d in domains
                    if (not group or metadata.get(d['domain'], {}).get('group') == group) and
                    (not tag or tag in metadata.get(d['domain'], {}).get('tags', []))
                ]
            
            if export:
                export_domains(domains, metadata, export, output)
            else:
                table = Table(title="Domain Portfolio")
                table.add_column("Domain", style="cyan")
                table.add_column("Expiry Date", style="dim")
                table.add_column("Auto-Renewal", style="bold")
                table.add_column("Group", style="blue")
                table.add_column("Tags", style="green")
                
                for domain in domains:
                    domain_name = domain['domain']
                    meta = metadata.get(domain_name, {})
                    
                    table.add_row(
                        domain_name,
                        domain.get('expirationDate', 'N/A'),
                        "[green]Yes[/]" if domain.get('autoRenew') else "[red]No[/]",
                        meta.get('group', ''),
                        ", ".join(meta.get('tags', []))
                    )
                
                console.print(table)
        else:
            console.print(f"[error]Error retrieving domains: {result.get('message')}[/]")
    except Exception as e:
        console.print(f"[error]Error retrieving domains: {str(e)}[/]")

@portfolio.command()
@click.argument('domain')
@click.option('--group', help='Assign to group')
@click.option('--tags', help='Comma-separated list of tags')
def tag(domain: str, group: Optional[str], tags: Optional[str]):
    """Tag a domain or assign it to a group."""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        # Verify domain exists
        result = make_request(f"domain/getDomain/{domain}", {})
        if result.get('status') != 'SUCCESS':
            console.print(f"[error]Domain not found: {domain}[/]")
            return
            
        # Load and update metadata
        metadata = load_domain_metadata()
        domain_meta = metadata.get(domain, {})
        
        if group:
            domain_meta['group'] = group
            
        if tags:
            domain_meta['tags'] = [t.strip() for t in tags.split(',')]
            
        metadata[domain] = domain_meta
        save_domain_metadata(metadata)
        
        console.print(f"[success]Successfully updated metadata for {domain}[/]")
    except Exception as e:
        console.print(f"[error]Error updating domain metadata: {str(e)}[/]")

@portfolio.command()
def groups():
    """List domain groups."""
    try:
        metadata = load_domain_metadata()
        groups = {}
        
        for domain, meta in metadata.items():
            group = meta.get('group')
            if group:
                groups.setdefault(group, []).append(domain)
        
        if not groups:
            console.print("[info]No domain groups found[/]")
            return
            
        table = Table(title="Domain Groups")
        table.add_column("Group", style="blue")
        table.add_column("Domains", style="cyan")
        table.add_column("Count", justify="right", style="green")
        
        for group, domains in sorted(groups.items()):
            table.add_row(
                group,
                ", ".join(domains[:3] + ["..."] if len(domains) > 3 else domains),
                str(len(domains))
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error listing groups: {str(e)}[/]")

@portfolio.command()
def tags():
    """List domain tags."""
    try:
        metadata = load_domain_metadata()
        tags = {}
        
        for domain, meta in metadata.items():
            for tag in meta.get('tags', []):
                tags.setdefault(tag, []).append(domain)
        
        if not tags:
            console.print("[info]No domain tags found[/]")
            return
            
        table = Table(title="Domain Tags")
        table.add_column("Tag", style="green")
        table.add_column("Domains", style="cyan")
        table.add_column("Count", justify="right", style="blue")
        
        for tag, domains in sorted(tags.items()):
            table.add_row(
                tag,
                ", ".join(domains[:3] + ["..."] if len(domains) > 3 else domains),
                str(len(domains))
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error listing tags: {str(e)}[/]")

def load_domain_metadata() -> Dict:
    """Load domain metadata from file."""
    metadata_file = Path.home() / '.porkbun' / 'metadata.json'
    if metadata_file.exists():
        with open(metadata_file) as f:
            return json.load(f)
    return {}

def save_domain_metadata(metadata: Dict):
    """Save domain metadata to file."""
    metadata_file = Path.home() / '.porkbun' / 'metadata.json'
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

def export_transactions(transactions: List[Dict], format: str, output: Optional[str]):
    """Export transactions to file."""
    output = output or f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
    
    if format == 'json':
        with open(output, 'w') as f:
            json.dump(transactions, f, indent=2)
    else:  # csv
        import csv
        with open(output, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'description', 'amount', 'type'])
            writer.writeheader()
            for tx in transactions:
                amount = float(tx.get('amount', 0))
                writer.writerow({
                    'date': tx.get('date', ''),
                    'description': tx.get('description', ''),
                    'amount': f"${abs(amount):.2f}",
                    'type': 'Credit' if amount > 0 else 'Debit'
                })
    
    console.print(f"[success]Transactions exported to {output}[/]")

def export_domains(domains: List[Dict], metadata: Dict, format: str, output: Optional[str]):
    """Export domains to file."""
    output = output or f"domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
    
    if format == 'json':
        export_data = []
        for domain in domains:
            domain_name = domain['domain']
            meta = metadata.get(domain_name, {})
            export_data.append({
                'domain': domain_name,
                'expiry': domain.get('expirationDate'),
                'auto_renew': domain.get('autoRenew'),
                'group': meta.get('group'),
                'tags': meta.get('tags', [])
            })
        
        with open(output, 'w') as f:
            json.dump(export_data, f, indent=2)
    else:  # csv
        import csv
        with open(output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Domain', 'Expiry Date', 'Auto-Renewal', 'Group', 'Tags'])
            
            for domain in domains:
                domain_name = domain['domain']
                meta = metadata.get(domain_name, {})
                writer.writerow([
                    domain_name,
                    domain.get('expirationDate', ''),
                    'Yes' if domain.get('autoRenew') else 'No',
                    meta.get('group', ''),
                    ', '.join(meta.get('tags', []))
                ])
    
    console.print(f"[success]Domains exported to {output}[/]")