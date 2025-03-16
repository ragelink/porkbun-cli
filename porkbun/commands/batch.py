"""Batch command execution for Porkbun CLI."""

import click
import asyncio
import yaml
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

@click.group()
def batch():
    """Batch command execution"""
    pass

@batch.command()
@click.argument("batch_file", type=click.Path(exists=True, readable=True))
@click.option("--stop-on-error/--continue-on-error", default=True, 
             help="Stop execution on first error or continue with remaining commands")
@click.option("--dry-run", is_flag=True, help="Print commands without executing them")
def run(batch_file: str, stop_on_error: bool, dry_run: bool):
    """Execute commands from a batch file.
    
    The batch file can be in YAML or JSON format and should contain a list of commands to execute.
    Each command should have a 'cmd' field and optionally a 'description' field.
    
    Example YAML file:
    ```yaml
    - cmd: porkbun dns retrieve example.com
      description: Retrieve DNS records
    - cmd: porkbun email list-forwards example.com
      description: List email forwards
    ```
    
    Example JSON file:
    ```json
    [
      {
        "cmd": "porkbun dns retrieve example.com",
        "description": "Retrieve DNS records"
      },
      {
        "cmd": "porkbun email list-forwards example.com",
        "description": "List email forwards"
      }
    ]
    ```
    """
    batch_path = Path(batch_file)
    
    # Load commands from batch file
    commands = _load_batch_file(batch_path)
    
    if not commands:
        console.print("[yellow]No commands found in batch file[/]")
        return
    
    console.print(f"[bold]Loaded {len(commands)} commands from {batch_path}[/]")
    
    if dry_run:
        _print_commands(commands)
        return
    
    # Execute commands
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[bold green]Executing commands...", total=len(commands))
        
        for i, command in enumerate(commands, 1):
            cmd = command["cmd"]
            description = command.get("description", cmd)
            
            progress.update(task, description=f"[bold green]({i}/{len(commands)}) {description}[/]")
            
            try:
                # Convert command string to list for subprocess
                cmd_parts = []
                if cmd.startswith("porkbun "):
                    # Replace "porkbun" with the actual Python module command
                    cmd_parts = [sys.executable, "-m", "porkbun.cli"] + cmd.split()[1:]
                else:
                    # Split the command into parts
                    cmd_parts = cmd.split()
                
                # Run the command
                result = subprocess.run(
                    cmd_parts,
                    capture_output=True,
                    text=True,
                    check=False  # Don't raise exception on non-zero exit code
                )
                
                if result.returncode == 0:
                    console.print(f"[green]✓ Command succeeded:[/] {description}")
                    if result.stdout.strip():
                        console.print(result.stdout.strip())
                else:
                    console.print(f"[red]✗ Command failed:[/] {description}")
                    if result.stderr.strip():
                        console.print(f"[red]Error:[/] {result.stderr.strip()}")
                    if stop_on_error:
                        console.print("[red]Stopping batch execution due to error[/]")
                        break
            except Exception as e:
                console.print(f"[red]✗ Error executing command:[/] {str(e)}")
                if stop_on_error:
                    console.print("[red]Stopping batch execution due to error[/]")
                    break
            
            progress.update(task, advance=1)
    
    console.print("[bold green]Batch execution completed[/]")

def _load_batch_file(file_path: Path) -> List[Dict[str, str]]:
    """Load commands from a batch file in YAML or JSON format."""
    content = file_path.read_text()
    
    if file_path.suffix.lower() in ('.yaml', '.yml'):
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            console.print(f"[red]Error parsing YAML file: {str(e)}[/]")
            return []
    elif file_path.suffix.lower() == '.json':
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error parsing JSON file: {str(e)}[/]")
            return []
    else:
        # Try to parse as YAML first, then as JSON
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                console.print(f"[red]Could not parse batch file as YAML or JSON[/]")
                return []

def _print_commands(commands: List[Dict[str, str]]):
    """Print commands without executing them (dry run)."""
    table = Table(title="Commands to Execute (Dry Run)")
    
    table.add_column("#", style="dim")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")
    
    for i, command in enumerate(commands, 1):
        cmd = command["cmd"]
        description = command.get("description", "")
        table.add_row(str(i), cmd, description)
    
    console.print(table)

@batch.command()
@click.argument("output_file", type=click.Path())
@click.option("--format", type=click.Choice(["yaml", "json"]), default="yaml", help="Output file format")
def create_template(output_file: str, format: str):
    """Create a template batch file.
    
    This command creates a template batch file with example commands.
    
    Example:
    porkbun batch create-template batch_commands.yaml
    """
    template = [
        {
            "cmd": "porkbun dns retrieve example.com",
            "description": "Retrieve DNS records for example.com"
        },
        {
            "cmd": "porkbun email list-forwards example.com",
            "description": "List email forwards for example.com"
        },
        {
            "cmd": "porkbun dns create-record example.com A 192.0.2.1 600 --name www",
            "description": "Create an A record for www.example.com"
        }
    ]
    
    output_path = Path(output_file)
    
    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write template to file
    if format == "yaml":
        output_path.write_text(yaml.dump(template, default_flow_style=False))
    else:
        output_path.write_text(json.dumps(template, indent=2))
    
    console.print(f"[green]Template batch file created at {output_path}[/]")

@batch.command()
@click.argument("command", nargs=-1, required=True)
@click.option("--output", type=click.Path(), help="Output batch file")
@click.option("--format", type=click.Choice(["yaml", "json"]), default="yaml", help="Output file format")
@click.option("--add-to", type=click.Path(exists=True), help="Add command to existing batch file")
def add(command: List[str], output: Optional[str], format: str, add_to: Optional[str]):
    """Add a command to a batch file.
    
    Example:
    porkbun batch add "porkbun dns retrieve example.com" --output batch_commands.yaml
    """
    cmd = " ".join(command)
    
    if add_to:
        # Add to existing file
        add_path = Path(add_to)
        commands = _load_batch_file(add_path)
        commands.append({"cmd": cmd})
        
        if add_path.suffix.lower() in ('.yaml', '.yml'):
            add_path.write_text(yaml.dump(commands, default_flow_style=False))
        else:
            add_path.write_text(json.dumps(commands, indent=2))
        
        console.print(f"[green]Command added to {add_path}[/]")
    elif output:
        # Create new file or overwrite existing
        output_path = Path(output)
        commands = [{"cmd": cmd}]
        
        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "yaml" or output_path.suffix.lower() in ('.yaml', '.yml'):
            output_path.write_text(yaml.dump(commands, default_flow_style=False))
        else:
            output_path.write_text(json.dumps(commands, indent=2))
        
        console.print(f"[green]Command saved to {output_path}[/]")
    else:
        # Just print the command
        console.print(f"[cyan]Command:[/] {cmd}")
        console.print("[yellow]Note: Use --output or --add-to to save this command to a batch file[/]")

if __name__ == "__main__":
    batch() 