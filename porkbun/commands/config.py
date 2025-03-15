import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from typing import Optional

from porkbun.utils.config import ConfigManager
from porkbun.utils.exceptions import ConfigError
from porkbun.utils.logging import logger

console = Console()
config_manager = ConfigManager()

@click.group()
def config():
    """Configuration management commands"""
    try:
        config_manager.load()
    except ConfigError as e:
        logger.debug("No existing configuration found")

@config.command()
@click.argument('name')
@click.option('--api-key', prompt=True, help='Porkbun API key')
@click.option('--secret-key', prompt=True, hide_input=True, help='Porkbun secret API key')
@click.option('--base-url', help='Custom API base URL')
@click.option('--make-default', is_flag=True, help='Set as default profile')
def add(name: str, api_key: str, secret_key: str, base_url: Optional[str], make_default: bool):
    """Add a new profile."""
    try:
        config_manager.add_profile(
            name=name,
            api_key=api_key,
            secret_key=secret_key,
            base_url=base_url,
            make_default=make_default
        )
        console.print(f"[success]Added profile: {name}[/]")
    except ConfigError as e:
        console.print(f"[error]{str(e)}[/]")

@config.command()
@click.argument('name')
def remove(name: str):
    """Remove a profile."""
    try:
        if Confirm.ask(f"Are you sure you want to remove profile '{name}'?"):
            config_manager.remove_profile(name)
            console.print(f"[success]Removed profile: {name}[/]")
    except ConfigError as e:
        console.print(f"[error]{str(e)}[/]")

@config.command()
@click.argument('name')
def use(name: str):
    """Switch to a different profile."""
    try:
        config_manager.set_current_profile(name)
        console.print(f"[success]Now using profile: {name}[/]")
    except ConfigError as e:
        console.print(f"[error]{str(e)}[/]")

@config.command()
def list():
    """List all profiles."""
    try:
        profiles = config_manager.list_profiles()
        if not profiles:
            console.print("[info]No profiles found[/]")
            return
            
        table = Table(title="Profiles")
        table.add_column("Name", style="cyan")
        table.add_column("Default", style="green")
        table.add_column("API Key", style="dim")
        table.add_column("Base URL", style="blue")
        
        current_profile = config_manager.current_profile
        
        for profile in profiles:
            name_display = f"[bold]{profile.name}[/]" if profile.name == current_profile else profile.name
            table.add_row(
                name_display,
                "✓" if profile.default else "",
                f"{profile.api_key[:8]}..." if profile.api_key else "Not set",
                profile.base_url
            )
        
        console.print(table)
    except ConfigError as e:
        console.print(f"[error]{str(e)}[/]")

@config.command()
def show():
    """Show current profile details."""
    try:
        profile = config_manager.get_profile()
        
        table = Table(title=f"Profile: {profile.name}")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("API Key", f"{profile.api_key[:8]}...")
        table.add_row("Secret Key", "********")
        table.add_row("Base URL", profile.base_url)
        table.add_row("Default", "Yes" if profile.default else "No")
        
        console.print(table)
    except ConfigError as e:
        console.print(f"[error]{str(e)}[/]")

@config.command()
def validate():
    """Validate current configuration."""
    try:
        config_manager.load()
        profile = config_manager.get_profile()
        
        table = Table(title="Configuration Status")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="green")
        
        table.add_row(
            "Configuration File",
            "[green]Valid[/]"
        )
        table.add_row(
            "Current Profile",
            f"[green]{profile.name}[/]"
        )
        table.add_row(
            "API Credentials",
            "[green]Present[/]"
        )
        
        console.print(table)
        console.print("[success]Configuration is valid[/]")
    except ConfigError as e:
        console.print(f"[error]Configuration error: {str(e)}[/]")
    except Exception as e:
        console.print(f"[error]Validation failed: {str(e)}[/]") 