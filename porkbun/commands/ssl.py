import click
import time
import asyncio
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from typing import Optional, Dict

from porkbun.api import make_request
from porkbun.utils.validation import validate_domain

console = Console()

@click.group()
def ssl():
    """SSL certificate management commands"""
    pass

@ssl.command()
@click.argument('domain')
@click.option('--save-path', type=click.Path(), help='Path to save certificate files')
def retrieve(domain: str, save_path: Optional[str]):
    """Retrieve SSL certificate for a domain."""
    if not validate_domain(domain):
        raise click.BadParameter("Invalid domain format")
        
    try:
        result = asyncio.run(make_request(f"ssl/retrieve/{domain}", {}))
        if result.get('status') == 'SUCCESS':
            cert_data = result.get('certificatechain', [])
            if not cert_data:
                console.print("[warning]No certificate found[/]")
                return
                
            # Print certificate info
            table = Table(title=f"SSL Certificate for {domain}")
            table.add_column("Type", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Expiry", style="dim")
            
            cert_info = result.get('intermediatecertificate', {})
            expiry = cert_info.get('notafter', 'Unknown')
            status = get_cert_status(expiry)
            
            table.add_row(
                cert_info.get('type', 'Standard'),
                status,
                expiry
            )
            
            console.print(table)
            
            # Save certificate files if requested
            if save_path:
                save_path = Path(save_path)
                save_path.mkdir(parents=True, exist_ok=True)
                
                # Save certificate chain
                for i, cert in enumerate(cert_data):
                    file_name = f"{domain}_{i}.crt"
                    with open(save_path / file_name, 'w') as f:
                        f.write(cert)
                
                # Save private key
                if result.get('privatekey'):
                    with open(save_path / f"{domain}.key", 'w') as f:
                        f.write(result['privatekey'])
                
                console.print(f"[success]Certificate files saved to {save_path}[/]")
                print_installation_guide(domain, save_path)
        else:
            console.print(f"[error]Error retrieving certificate: {result.get('message')}[/]")
    except Exception as e:
        console.print(f"[error]Error retrieving certificate: {str(e)}[/]")

@ssl.command()
@click.argument('domain')
@click.option('--save-path', type=click.Path(), help='Path to save certificate files')
@click.option('--force', is_flag=True, help='Force certificate regeneration')
def generate(domain: str, save_path: Optional[str], force: bool):
    """Generate SSL certificate for a domain."""
    raise click.ClickException("Not supported: Porkbun auto-generates SSL certificates; there is no generate endpoint. Use the ssl retrieve command to download the bundle.")

@ssl.command()
def list_all():
    """List all SSL certificates."""
    raise click.ClickException("Not supported: Porkbun's API (v3) has no ssl/listAll endpoint. Retrieve a specific domain's bundle with the ssl retrieve command.")

@ssl.command()
def expiring():
    """List certificates expiring soon."""
    raise click.ClickException("Not supported: Porkbun's API (v3) has no ssl/listAll endpoint. Retrieve a specific domain's bundle with the ssl retrieve command.")

def get_cert_status(expiry: str) -> str:
    """Get certificate status based on expiry date."""
    try:
        expiry_time = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
        days_until_expiry = (expiry_time.timestamp() - time.time()) / (24 * 60 * 60)
        
        if days_until_expiry <= 0:
            return "[red]Expired[/]"
        elif days_until_expiry <= 7:
            return "[red]Expiring Soon[/]"
        elif days_until_expiry <= 14:
            return "[yellow]Expiring Soon[/]"
        else:
            return "[green]Active[/]"
    except ValueError:
        return "[yellow]Unknown[/]"

def print_installation_guide(domain: str, cert_path: Path):
    """Print SSL certificate installation guide."""
    guide = f"""
# SSL Certificate Installation Guide for {domain}

Your SSL certificate files have been saved to: {cert_path}

## Files
- `{domain}_0.crt`: Main certificate
- `{domain}_1.crt`: Intermediate certificate
- `{domain}.key`: Private key

## Installation Instructions

### Nginx
```nginx
ssl_certificate {cert_path}/{domain}_0.crt;
ssl_certificate_key {cert_path}/{domain}.key;
ssl_trusted_certificate {cert_path}/{domain}_1.crt;
```

### Apache
```apache
SSLCertificateFile {cert_path}/{domain}_0.crt
SSLCertificateKeyFile {cert_path}/{domain}.key
SSLCertificateChainFile {cert_path}/{domain}_1.crt
```

### Other Web Servers
For other web servers, you may need to concatenate the certificates:
```bash
cat {domain}_0.crt {domain}_1.crt > {domain}_chain.crt
```

## Security Best Practices
1. Set proper permissions: `chmod 600` for the private key
2. Keep backups of your certificates
3. Monitor certificate expiration
4. Enable HSTS if possible
5. Configure strong SSL protocols and ciphers

Need help? Visit https://porkbun.com/ssl for more information.
"""
    
    console.print(Markdown(guide))