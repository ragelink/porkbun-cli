import click
import yaml
import json
import schedule
import requests
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from typing import Dict, Any, Optional, List
import subprocess
import threading
import time

from porkbun.utils.logging import logger
from porkbun.utils.validation import validate_domain

console = Console()

@click.group()
def automation():
    """Automation and scheduling commands"""
    pass

@automation.command()
@click.argument('script_path', type=click.Path(exists=True))
@click.option('--vars', '-v', multiple=True, help='Variables in key=value format')
@click.option('--dry-run', is_flag=True, help='Show what would be executed')
def script(script_path: str, vars: List[str], dry_run: bool):
    """Run automation scripts."""
    try:
        with open(script_path) as f:
            script_data = yaml.safe_load(f)
        
        # Parse variables
        variables = {}
        for var in vars:
            key, value = var.split('=', 1)
            variables[key.strip()] = value.strip()
            
        # Validate script structure
        if not isinstance(script_data, dict) or 'steps' not in script_data:
            raise ValueError("Invalid script format: must contain 'steps' key")
            
        # Process steps
        steps = script_data['steps']
        for i, step in enumerate(steps, 1):
            command = step.get('command')
            if not command:
                continue
                
            # Replace variables
            for key, value in variables.items():
                command = command.replace(f"${key}", value)
                
            if dry_run:
                console.print(f"[cyan]Step {i}:[/] Would execute: {command}")
                continue
                
            console.print(f"[cyan]Step {i}:[/] Executing: {command}")
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    console.print("[green]Success[/]")
                    if result.stdout:
                        console.print(result.stdout)
                else:
                    console.print(f"[red]Failed (exit code {result.returncode})[/]")
                    if result.stderr:
                        console.print(result.stderr)
                        
                # Handle step failure
                if result.returncode != 0 and step.get('fail_fast', True):
                    console.print("[red]Stopping due to step failure[/]")
                    break
                    
            except Exception as e:
                console.print(f"[red]Error executing step: {e}[/]")
                if step.get('fail_fast', True):
                    break
                    
    except Exception as e:
        logger.error(f"Error running script: {e}")
        console.print(f"[error]Error: {str(e)}[/]")

@automation.command()
@click.argument('webhook_url')
@click.option('--event', '-e', required=True, help='Event to trigger webhook')
@click.option('--data', '-d', help='JSON data to send')
@click.option('--test', is_flag=True, help='Test webhook without executing')
def webhook(webhook_url: str, event: str, data: Optional[str], test: bool):
    """Configure and test webhooks."""
    try:
        payload = {
            'event': event,
            'timestamp': datetime.now().isoformat(),
            'data': json.loads(data) if data else {}
        }
        
        if test:
            console.print("Test payload:")
            console.print(Syntax(json.dumps(payload, indent=2), "json"))
            return
            
        response = requests.post(webhook_url, json=payload)
        if response.ok:
            console.print("[success]Webhook delivered successfully[/]")
            console.print(f"Response: {response.status_code}")
            if response.text:
                console.print(response.text)
        else:
            console.print(f"[error]Webhook failed: {response.status_code}[/]")
            console.print(response.text)
            
    except Exception as e:
        logger.error(f"Error with webhook: {e}")
        console.print(f"[error]Error: {str(e)}[/]")

@automation.command()
@click.argument('schedule_file', type=click.Path(exists=True))
@click.option('--list', 'list_tasks', is_flag=True, help='List scheduled tasks')
@click.option('--clear', is_flag=True, help='Clear all scheduled tasks')
def scheduler(schedule_file: str, list_tasks: bool, clear: bool):
    """Manage scheduled tasks."""
    try:
        if clear:
            schedule.clear()
            console.print("[success]All scheduled tasks cleared[/]")
            return
            
        if list_tasks:
            jobs = schedule.get_jobs()
            if not jobs:
                console.print("[info]No scheduled tasks[/]")
                return
                
            table = Table(title="Scheduled Tasks")
            table.add_column("Task", style="cyan")
            table.add_column("Schedule", style="green")
            table.add_column("Next Run", style="yellow")
            
            for job in jobs:
                table.add_row(
                    str(job.job_func.__name__),
                    str(job),
                    job.next_run.strftime("%Y-%m-%d %H:%M:%S")
                )
                
            console.print(table)
            return
            
        with open(schedule_file) as f:
            tasks = yaml.safe_load(f)
            
        if not isinstance(tasks, dict) or 'tasks' not in tasks:
            raise ValueError("Invalid schedule format: must contain 'tasks' key")
            
        def run_scheduled_tasks():
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        for task in tasks['tasks']:
            name = task.get('name', 'unnamed_task')
            when = task.get('when')
            command = task.get('command')
            
            if not when or not command:
                logger.warning(f"Skipping invalid task: {name}")
                continue
                
            def job_func(cmd=command):
                try:
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        logger.info(f"Task succeeded: {cmd}")
                    else:
                        logger.error(f"Task failed: {cmd}")
                except Exception as e:
                    logger.error(f"Error in scheduled task: {e}")
                    
            # Schedule based on 'when' specification
            if when == 'daily':
                schedule.every().day.do(job_func)
            elif when.startswith('every '):
                parts = when.split()
                if len(parts) >= 3:
                    interval = int(parts[1])
                    unit = parts[2]
                    if unit == 'minutes':
                        schedule.every(interval).minutes.do(job_func)
                    elif unit == 'hours':
                        schedule.every(interval).hours.do(job_func)
            else:
                schedule.every().day.at(when).do(job_func)
                
        console.print("[success]Tasks scheduled successfully[/]")
        console.print("[info]Starting scheduler (Press Ctrl+C to stop)[/]")
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
        scheduler_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[info]Scheduler stopped[/]")
            
    except Exception as e:
        logger.error(f"Error with scheduler: {e}")
        console.print(f"[error]Error: {str(e)}[/]") 