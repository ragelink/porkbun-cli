import click
from rich.console import Console
from pathlib import Path
from typing import Optional

from porkbun.commands.domains import domains
from porkbun.commands.dns import dns
from porkbun.commands.ssl import ssl
from porkbun.commands.account import account
from porkbun.commands.config import config
from porkbun.commands.monitor import monitor
from porkbun.commands.automation import automation
from porkbun.commands.url import url
from porkbun.commands.email import email
from porkbun.commands.workflow import workflow
from porkbun.commands.batch import batch
from porkbun.utils.logging import setup_logging, logger
from porkbun.utils.config import ConfigManager

__version__ = '0.2.0'

console = Console()
config_manager = ConfigManager()

@click.group()
@click.version_option(version=__version__, prog_name='porkbun-cli')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--log-file', type=click.Path(), help='Path to log file')
@click.option('--profile', help='Use specific profile')
def cli(debug: bool, log_file: Optional[str], profile: Optional[str]):
    """Porkbun CLI - Manage your domains and DNS records"""
    setup_logging(debug=debug, log_file=log_file)
    logger.debug("Starting Porkbun CLI")
    
    try:
        config_manager.load()
        if profile:
            config_manager.set_current_profile(profile)
    except Exception as e:
        logger.debug(f"Configuration error: {e}")

cli.add_command(domains)
cli.add_command(dns)
cli.add_command(ssl)
cli.add_command(account)
cli.add_command(config)
cli.add_command(monitor)
cli.add_command(automation)
cli.add_command(url)
cli.add_command(email)
cli.add_command(workflow)
cli.add_command(batch)

if __name__ == '__main__':
    cli()