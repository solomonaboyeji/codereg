"""Main CLI entry point."""

import os
import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from pathlib import Path

from .agent import Agent
from .ollama_client import OllamaClient


console = Console()


@click.group(invoke_without_command=True)
@click.option('--model', '-m', default='qwen3-coder:30b', help='Ollama model to use')
@click.option('--url', '-u', default='http://localhost:11434', help='Ollama API URL')
@click.option('--project-dir', '-d', default='.', help='Project directory to work in')
@click.pass_context
def cli(ctx, model, url, project_dir):
    """AI CLI - Code modification using Ollama models.

    A Claude Code-like CLI tool that uses local Ollama models to read and modify code.
    """
    ctx.ensure_object(dict)
    ctx.obj['model'] = model
    ctx.obj['url'] = url
    ctx.obj['project_dir'] = project_dir

    # If no subcommand, show help
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            "[bold cyan]AI CLI[/bold cyan] - Code modification with Ollama\n\n"
            "Commands:\n"
            "  [green]aicli chat[/green]          Start interactive chat mode\n"
            "  [green]aicli ask 'question'[/green]   Ask a single question\n"
            "  [green]aicli models[/green]        List available models\n\n"
            "Options:\n"
            "  [yellow]--model, -m[/yellow]       Model to use (default: qwen3-coder:30b)\n"
            "  [yellow]--url, -u[/yellow]         Ollama API URL (default: http://localhost:11434)\n"
            "  [yellow]--project-dir, -d[/yellow] Project directory (default: current dir)\n\n"
            "Examples:\n"
            "  aicli chat\n"
            "  aicli ask 'Read main.py and add error handling'\n"
            "  aicli -m qwen3:30b ask 'Find all Python files'",
            title="🤖 Welcome to AI CLI",
            border_style="cyan"
        ))


@cli.command()
@click.pass_context
def models(ctx):
    """List available Ollama models."""
    url = ctx.obj['url']

    try:
        client = OllamaClient(base_url=url)
        model_list = client.list_models()

        if model_list:
            console.print("\n[bold cyan]Available Models:[/bold cyan]\n")
            for model in model_list:
                console.print(f"  • {model}")
            console.print()
        else:
            console.print("[yellow]No models found. Run 'ollama pull <model>' to download models.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error connecting to Ollama: {str(e)}[/red]")
        console.print("[yellow]Make sure Ollama is running: 'ollama serve'[/yellow]")


@cli.command()
@click.argument('message', required=False)
@click.option('--debug', is_flag=True, help='Enable debug output')
@click.option('--no-stream', is_flag=True, help='Disable streaming for better tool calling')
@click.pass_context
def ask(ctx, message, debug, no_stream):
    """Ask a single question or give a single instruction."""
    model = ctx.obj['model']
    url = ctx.obj['url']
    project_dir = ctx.obj['project_dir']

    if not message:
        console.print("[red]Error: Please provide a message[/red]")
        console.print("Example: aicli ask 'Read main.py and add error handling'")
        return

    try:
        # Check if model exists
        client = OllamaClient(base_url=url, model=model)
        if not client.check_model_exists(model):
            console.print(f"[red]Error: Model '{model}' not found[/red]")
            console.print(f"[yellow]Available models:[/yellow]")
            for m in client.list_models():
                console.print(f"  • {m}")
            return

        console.print(Panel(
            f"[cyan]Model:[/cyan] {model}\n"
            f"[cyan]Project:[/cyan] {project_dir}\n"
            f"[cyan]Query:[/cyan] {message}",
            title="🤖 AI CLI",
            border_style="cyan"
        ))
        console.print()

        # Create agent and run
        agent = Agent(
            ollama_url=url,
            model=model,
            project_dir=project_dir,
            debug=debug
        )

        agent.run(message, stream=not no_stream)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
@click.pass_context
def chat(ctx):
    """Start interactive chat mode."""
    model = ctx.obj['model']
    url = ctx.obj['url']
    project_dir = ctx.obj['project_dir']

    try:
        # Check if model exists
        client = OllamaClient(base_url=url, model=model)
        if not client.check_model_exists(model):
            console.print(f"[red]Error: Model '{model}' not found[/red]")
            console.print(f"[yellow]Available models:[/yellow]")
            for m in client.list_models():
                console.print(f"  • {m}")
            return

        console.print(Panel(
            f"[bold cyan]Interactive Chat Mode[/bold cyan]\n\n"
            f"[cyan]Model:[/cyan] {model}\n"
            f"[cyan]Project:[/cyan] {project_dir}\n\n"
            f"Type your messages and press Enter. The AI can read, edit, and create files.\n\n"
            f"Commands:\n"
            f"  [green]/clear[/green]  - Clear conversation history\n"
            f"  [green]/quit[/green]   - Exit chat mode\n"
            f"  [green]Ctrl+C[/green]  - Exit chat mode",
            title="🤖 AI CLI - Chat Mode",
            border_style="cyan"
        ))
        console.print()

        # Create agent
        agent = Agent(
            ollama_url=url,
            model=model,
            project_dir=project_dir
        )

        # Create prompt session with history
        history_file = Path.home() / ".aicli_history"
        session = PromptSession(history=FileHistory(str(history_file)))

        while True:
            try:
                # Get user input
                user_input = session.prompt("\n> ")

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.strip() == "/quit":
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                elif user_input.strip() == "/clear":
                    agent.clear_history()
                    continue

                # Run agent
                console.print()
                agent.run(user_input, stream=True)

            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except EOFError:
                console.print("\n[yellow]Goodbye![/yellow]")
                break

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == '__main__':
    cli(obj={})
