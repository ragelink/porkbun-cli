import click
import dns.resolver
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import List, Dict, Any, Optional
import json

from porkbun.api import make_request
from porkbun.utils.logging import logger
from porkbun.utils.validation import validate_domain

console = Console()

@click.group()
def monitor():
    """Domain monitoring commands"""
    pass

@monitor.command()
@click.option('--days', type=int, default=30, help='Days until expiration to check')
@click.option('--notify/--no-notify', default=True, help='Enable/disable notifications')
@click.option('--export', type=click.Choice(['json', 'csv']), help='Export results')
@click.option('--output', type=click.Path(), help='Output file path')
def expiring(days: int, notify: bool, export: Optional[str], output: Optional[str]):
    """Monitor domains expiring soon."""
    try:
        result = make_request("domain/listAll", {})
        if result.get('status') != 'SUCCESS':
            console.print("[error]Failed to retrieve domains[/]")
            return
            
        domains = result.get('domains', [])
        expiring_domains = []
        current_time = datetime.now()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Checking domain expiration...", total=len(domains))
            
            for domain in domains:
                progress.update(task, advance=1)
                expiry_str = domain.get('expirationDate')
                if not expiry_str:
                    continue
                    
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
                    days_left = (expiry_date - current_time).days
                    
                    if days_left <= days:
                        expiring_domains.append({
                            'domain': domain['domain'],
                            'expiry_date': expiry_str,
                            'days_left': days_left
                        })
                except ValueError:
                    logger.error(f"Invalid date format for domain {domain['domain']}")
        
        if not expiring_domains:
            console.print(f"[info]No domains expiring in the next {days} days[/]")
            return
            
        if export:
            export_results(expiring_domains, export, output)
        else:
            table = Table(title=f"Domains Expiring in {days} Days")
            table.add_column("Domain", style="cyan")
            table.add_column("Expiry Date", style="dim")
            table.add_column("Days Left", justify="right")
            
            for domain in sorted(expiring_domains, key=lambda x: x['days_left']):
                days_style = "red" if domain['days_left'] <= 7 else "yellow"
                table.add_row(
                    domain['domain'],
                    domain['expiry_date'],
                    f"[{days_style}]{domain['days_left']}[/]"
                )
            
            console.print(table)
            
        if notify and expiring_domains:
            # TODO: Implement notification system
            pass
            
    except Exception as e:
        logger.error(f"Error checking expiring domains: {e}")
        console.print(f"[error]Error: {str(e)}[/]")

@monitor.command()
@click.argument('domain')
@click.option('--record-type', '-t', default='A', help='DNS record type to check')
@click.option('--nameservers', '-n', multiple=True, help='Specific nameservers to check')
@click.option('--interval', '-i', type=int, default=60, help='Check interval in seconds')
@click.option('--timeout', type=int, default=3600, help='Total timeout in seconds')
def propagation(domain: str, record_type: str, nameservers: List[str],
                interval: int, timeout: int):
    """Check DNS propagation status."""
    if not validate_domain(domain):
        console.print("[error]Invalid domain format[/]")
        return
        
    try:
        # Get default nameservers if none specified
        if not nameservers:
            ns_result = make_request(f"dns/retrieveNameServers/{domain}", {})
            if ns_result.get('status') == 'SUCCESS':
                nameservers = ns_result.get('nameservers', [])
            
        if not nameservers:
            console.print("[error]No nameservers found[/]")
            return
            
        resolver = dns.resolver.Resolver()
        start_time = time.time()
        consistent = False
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Checking DNS propagation...", total=None)
            
            while time.time() - start_time < timeout:
                results = {}
                all_match = True
                
                for ns in nameservers:
                    resolver.nameservers = [ns]
                    try:
                        answers = resolver.resolve(domain, record_type)
                        results[ns] = [str(rdata) for rdata in answers]
                    except Exception as e:
                        results[ns] = [f"Error: {str(e)}"]
                        all_match = False
                
                # Check if all nameservers return the same results
                first_result = next(iter(results.values()))
                for result in results.values():
                    if set(result) != set(first_result):
                        all_match = False
                        break
                
                if all_match:
                    consistent = True
                    break
                
                time.sleep(interval)
            
            progress.update(task, completed=True)
        
        if consistent:
            console.print("[success]DNS propagation complete[/]")
        else:
            console.print("[warning]DNS propagation incomplete or inconsistent[/]")
        
        table = Table(title="DNS Propagation Results")
        table.add_column("Nameserver", style="cyan")
        table.add_column("Records", style="green")
        
        for ns, records in results.items():
            table.add_row(ns, "\n".join(records))
        
        console.print(table)
        
    except Exception as e:
        logger.error(f"Error checking DNS propagation: {e}")
        console.print(f"[error]Error: {str(e)}[/]")

@monitor.command()
@click.argument('domain')
@click.option('--protocol', type=click.Choice(['http', 'https']), default='https')
@click.option('--port', type=int, help='Custom port')
@click.option('--path', default='/', help='Path to check')
@click.option('--interval', type=int, default=300, help='Check interval in seconds')
@click.option('--expect-status', type=int, default=200, help='Expected HTTP status')
@click.option('--timeout', type=int, default=30, help='Request timeout in seconds')
def health(domain: str, protocol: str, port: Optional[int], path: str,
           interval: int, expect_status: int, timeout: int):
    """Monitor domain health."""
    if not validate_domain(domain):
        console.print("[error]Invalid domain format[/]")
        return
        
    try:
        url = f"{protocol}://{domain}"
        if port:
            url = f"{url}:{port}"
        url = f"{url}{path}"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Monitoring health...", total=None)
            
            while True:
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=timeout)
                    response_time = time.time() - start_time
                    
                    status_style = "green" if response.status_code == expect_status else "red"
                    time_style = "green" if response_time < 1.0 else "yellow"
                    
                    progress.update(
                        task,
                        description=(
                            f"Status: [{status_style}]{response.status_code}[/] | "
                            f"Response Time: [{time_style}]{response_time:.2f}s[/]"
                        )
                    )
                except requests.exceptions.RequestException as e:
                    progress.update(
                        task,
                        description=f"[red]Error: {str(e)}[/]"
                    )
                
                time.sleep(interval)
                
    except KeyboardInterrupt:
        console.print("\n[info]Health monitoring stopped[/]")
    except Exception as e:
        logger.error(f"Error monitoring health: {e}")
        console.print(f"[error]Error: {str(e)}[/]")

def export_results(data: List[Dict[str, Any]], format: str, output: Optional[str]):
    """Export monitoring results."""
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"monitoring_{timestamp}.{format}"
    
    try:
        if format == 'json':
            with open(output, 'w') as f:
                json.dump(data, f, indent=2)
        else:  # csv
            import csv
            with open(output, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        console.print(f"[success]Results exported to {output}[/]")
    except Exception as e:
        logger.error(f"Error exporting results: {e}")
        console.print(f"[error]Failed to export results: {str(e)}[/]") 