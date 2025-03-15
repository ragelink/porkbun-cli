import click
from rich.console import Console
from porkbun.commands.email import email

console = Console()
console.print("[green]Successfully imported email module![/]")
console.print("[blue]Available commands:[/]")

for command in email.commands:
    console.print(f"[yellow]{command.name}[/]: {command.help}") 