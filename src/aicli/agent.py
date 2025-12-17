"""AI Agent that orchestrates tool calling and conversation."""

import json
import re
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm

from .ollama_client import OllamaClient, ConversationManager
from .tools import ToolRegistry


# Tools that require user permission before execution
PERMISSION_REQUIRED_TOOLS = {
    "write_file",
    "edit_file",
    "bash"
}

SYSTEM_PROMPT = """You are an AI coding assistant that helps users modify and understand code projects.

⚠️ CRITICAL: You MUST use tools to make changes. NEVER just write code in your response!

Available tools:
- read_file: Read file contents with optional line ranges
- write_file: Create or overwrite files with new content
- edit_file: Edit files by replacing specific text with new text
- grep: Search for patterns in files using regex
- glob: Find files matching glob patterns
- bash: Execute bash commands

🚫 FORBIDDEN BEHAVIOR:
- DO NOT write code directly in your response
- DO NOT show what the file "should look like"
- DO NOT describe changes without making them
- DO NOT output HTML/code without using write_file or edit_file

✅ REQUIRED BEHAVIOR:
1. When asked to create/modify a file → You MUST call write_file or edit_file
2. NEVER show code in your response - ALWAYS use the tools
3. After using tools, briefly confirm what you did

Example - WRONG ❌:
User: "Make the products section responsive"
You: "I'll create a responsive section: <div class='products'>...</div>"

Example - CORRECT ✅:
User: "Make the products section responsive"
You: [CALL read_file to see current code]
You: [CALL write_file with the updated responsive code]
You: "I've updated the products section to be responsive using CSS Grid and media queries."

REMEMBER: Use tools to modify files, don't just talk about it!"""


def contains_code_output(text: str) -> bool:
    """Detect if the model is outputting code instead of using tools."""
    # Check for common code patterns
    code_patterns = [
        r'```(?:html|css|javascript|python|js)',  # Code blocks
        r'<!DOCTYPE html>',  # HTML documents
        r'<html[\s>]',  # HTML tags
        r'def \w+\([^)]*\):',  # Python functions
        r'function \w+\(',  # JavaScript functions
        r'class \w+[:{]',  # Class definitions
    ]

    for pattern in code_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    # Check if response is very long (likely code dump)
    if len(text) > 1000 and '<' in text and '>' in text:
        return True

    return False


def parse_xml_tool_calls(text: str) -> list:
    """Parse XML-style tool calls from model output.

    Some models generate XML-like function calls instead of JSON.
    This function parses them and converts to proper tool call format.
    """
    tool_calls = []

    # Pattern to match <function=name> <parameter=key>value</parameter> </function>
    function_pattern = r'<function=(\w+)>(.*?)</function>'
    param_pattern = r'<parameter=(\w+)>(.*?)</parameter>'

    matches = re.finditer(function_pattern, text, re.DOTALL)

    for idx, match in enumerate(matches):
        function_name = match.group(1)
        params_text = match.group(2)

        # Extract parameters
        arguments = {}
        param_matches = re.finditer(param_pattern, params_text, re.DOTALL)
        for param_match in param_matches:
            param_name = param_match.group(1)
            param_value = param_match.group(2).strip()
            arguments[param_name] = param_value

        tool_call = {
            "id": f"xml_call_{idx}",
            "function": {
                "name": function_name,
                "arguments": arguments
            }
        }
        tool_calls.append(tool_call)

    return tool_calls


class Agent:
    """AI Agent that can read, modify, and understand code."""

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "qwen3-coder:30b",
        project_dir: str = ".",
        max_iterations: int = 100,
        debug: bool = False,
        auto_approve: bool = False
    ):
        self.client = OllamaClient(base_url=ollama_url, model=model)
        self.tools = ToolRegistry()

        # Use a persistent conversation history file
        history_file = Path.home() / ".aicli_conversation.json"
        self.conversation = ConversationManager(SYSTEM_PROMPT, history_file=str(history_file))

        self.console = Console()
        self.project_dir = project_dir
        self.max_iterations = max_iterations
        self.debug = debug
        self.auto_approve = auto_approve

    def run(self, user_message: str, stream: bool = True) -> str:
        """Run the agent with a user message.

        Args:
            user_message: The user's request
            stream: Whether to stream the response

        Returns:
            The final response from the agent
        """
        self.conversation.add_user_message(user_message)

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1

            # Get response from model
            try:
                response = self.client.chat(
                    messages=self.conversation.get_messages(),
                    tools=self.tools.get_all_schemas(),
                    stream=stream
                )

                if stream:
                    assistant_message, tool_calls = self._handle_streaming_response(response)
                else:
                    message = response.get("message", {})
                    assistant_message = message.get("content", "")
                    tool_calls = message.get("tool_calls", [])

                    if assistant_message:
                        self.console.print(Markdown(assistant_message))

                # Debug output
                if self.debug:
                    self.console.print(f"[dim]Debug: Got {len(tool_calls)} tool calls[/dim]")
                    if tool_calls:
                        self.console.print(f"[dim]Debug: Tool calls = {tool_calls}[/dim]")

                # Fallback: Check for XML-style tool calls in the message
                if not tool_calls and assistant_message:
                    xml_calls = parse_xml_tool_calls(assistant_message)
                    if xml_calls:
                        if self.debug:
                            self.console.print(f"[dim cyan]Debug: Parsed {len(xml_calls)} XML-style tool calls[/dim cyan]")
                        tool_calls = xml_calls
                        # Remove the XML from the displayed message
                        clean_message = re.sub(r'<function=.*?</function>', '', assistant_message, flags=re.DOTALL)
                        assistant_message = clean_message.strip()

                # Check if model is outputting code instead of using tools
                if not tool_calls and assistant_message and contains_code_output(assistant_message):
                    self.console.print(
                        Panel(
                            "[yellow]⚠️  Model generated code instead of using tools. Redirecting...[/yellow]",
                            border_style="yellow"
                        )
                    )
                    # Add a follow-up message to force tool use
                    self.conversation.add_assistant_message(assistant_message, [])
                    self.conversation.add_user_message(
                        "STOP! You just wrote code in your response instead of using the write_file or edit_file tool. "
                        "You MUST use the tools to actually modify the files. "
                        "Please use write_file or edit_file RIGHT NOW to make the changes you described."
                    )
                    continue  # Continue the loop to get the tool call

                # Add assistant message to conversation
                self.conversation.add_assistant_message(assistant_message, tool_calls)

                # If no tool calls, we're done
                if not tool_calls:
                    if self.debug:
                        self.console.print("[dim yellow]Debug: No tool calls, ending loop[/dim yellow]")
                    return assistant_message

                # Execute tool calls
                self._execute_tool_calls(tool_calls)

            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")
                return f"Error occurred: {str(e)}"

        self.console.print("[yellow]Warning: Maximum iterations reached[/yellow]")
        return "Maximum iterations reached"

    def _handle_streaming_response(self, response_stream) -> tuple[str, list]:
        """Handle streaming response from Ollama.

        Returns:
            Tuple of (assistant_message, tool_calls)
        """
        assistant_message = ""
        tool_calls = []
        current_content = ""

        for chunk in response_stream:
            if self.debug:
                self.console.print(f"\n[dim]Debug chunk: {chunk}[/dim]\n", end="")

            message = chunk.get("message", {})

            # Accumulate content
            if "content" in message:
                content = message["content"]
                current_content += content
                self.console.print(content, end="")

            # Check for tool calls - accumulate them
            if "tool_calls" in message:
                new_calls = message["tool_calls"]
                if new_calls:
                    tool_calls.extend(new_calls) if isinstance(new_calls, list) else tool_calls.append(new_calls)
                if self.debug:
                    self.console.print(f"\n[dim]Debug: Found tool_calls in chunk: {new_calls}[/dim]\n", end="")

            # Check if done
            if chunk.get("done", False):
                assistant_message = current_content
                if assistant_message:
                    self.console.print()  # New line after streaming
                break

        return assistant_message, tool_calls

    def _execute_tool_calls(self, tool_calls: list):
        """Execute tool calls and add results to conversation."""
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            tool_name = function.get("name")
            arguments = function.get("arguments", {})

            # Parse arguments if they're a string
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}

            self.console.print(
                Panel(
                    f"[cyan]Tool:[/cyan] {tool_name}\n"
                    f"[cyan]Args:[/cyan] {json.dumps(arguments, indent=2)}",
                    title="🔧 Tool Call",
                    border_style="cyan"
                )
            )

            # Check if permission is required
            if tool_name in PERMISSION_REQUIRED_TOOLS:
                if not self._request_permission(tool_name, arguments):
                    result = {"error": "Permission denied by user"}
                    self.console.print(
                        Panel(
                            "[yellow]⚠️  Tool execution cancelled by user[/yellow]",
                            title="❌ Permission Denied",
                            border_style="yellow"
                        )
                    )
                    # Add result to conversation
                    tool_call_id = tool_call.get("id", "")
                    self.conversation.add_tool_result(tool_call_id, tool_name, result)
                    continue

            # Execute the tool
            result = self.tools.execute_tool(tool_name, **arguments)

            # Display result
            self._display_tool_result(tool_name, result)

            # Add result to conversation
            tool_call_id = tool_call.get("id", "")
            self.conversation.add_tool_result(tool_call_id, tool_name, result)

    def _request_permission(self, tool_name: str, arguments: dict) -> bool:
        """Request user permission before executing a tool.

        Args:
            tool_name: The name of the tool to execute
            arguments: The arguments for the tool

        Returns:
            True if permission granted, False otherwise
        """
        # Auto-approve if enabled
        if self.auto_approve:
            return True

        # Format the permission prompt based on the tool
        if tool_name == "write_file":
            file_path = arguments.get("file_path", "unknown")
            content_preview = arguments.get("content", "")[:100]
            if len(arguments.get("content", "")) > 100:
                content_preview += "..."

            self.console.print(
                Panel(
                    f"[yellow]File:[/yellow] {file_path}\n"
                    f"[yellow]Preview:[/yellow] {content_preview}",
                    title="⚠️  Write File Permission",
                    border_style="yellow"
                )
            )
            return Confirm.ask("[bold yellow]Allow write to this file?[/bold yellow]", default=True)

        elif tool_name == "edit_file":
            file_path = arguments.get("file_path", "unknown")
            old_text = arguments.get("old_text", "")[:50]
            new_text = arguments.get("new_text", "")[:50]
            if len(arguments.get("old_text", "")) > 50:
                old_text += "..."
            if len(arguments.get("new_text", "")) > 50:
                new_text += "..."

            self.console.print(
                Panel(
                    f"[yellow]File:[/yellow] {file_path}\n"
                    f"[yellow]Replace:[/yellow] {old_text}\n"
                    f"[yellow]With:[/yellow] {new_text}",
                    title="⚠️  Edit File Permission",
                    border_style="yellow"
                )
            )
            return Confirm.ask("[bold yellow]Allow this file edit?[/bold yellow]", default=True)

        elif tool_name == "bash":
            command = arguments.get("command", "unknown")

            self.console.print(
                Panel(
                    f"[yellow]Command:[/yellow] {command}",
                    title="⚠️  Bash Command Permission",
                    border_style="yellow"
                )
            )
            return Confirm.ask("[bold yellow]Allow this command to run?[/bold yellow]", default=True)

        # Default: ask for permission
        return Confirm.ask(f"[bold yellow]Allow {tool_name}?[/bold yellow]", default=True)

    def _display_tool_result(self, tool_name: str, result: dict):
        """Display tool execution result in a nice format."""
        if "error" in result:
            self.console.print(
                Panel(
                    f"[red]{result['error']}[/red]",
                    title=f"❌ {tool_name} - Error",
                    border_style="red"
                )
            )
        elif tool_name == "read_file":
            if "content" in result:
                # Show syntax highlighted content
                self.console.print(
                    Panel(
                        result["content"][:1000] + ("..." if len(result["content"]) > 1000 else ""),
                        title=f"✅ {tool_name} - {result.get('line_count', 0)} lines",
                        border_style="green"
                    )
                )
        elif tool_name in ["write_file", "edit_file"]:
            self.console.print(
                Panel(
                    f"[green]{result.get('message', 'Success')}[/green]",
                    title=f"✅ {tool_name}",
                    border_style="green"
                )
            )
        elif tool_name == "bash":
            output = result.get("stdout", "") + result.get("stderr", "")
            self.console.print(
                Panel(
                    output[:1000] + ("..." if len(output) > 1000 else ""),
                    title=f"✅ {tool_name}",
                    border_style="green"
                )
            )
        elif tool_name == "grep":
            matches = result.get("matches", [])
            total = result.get("total", 0)
            if matches:
                match_str = "\n".join(
                    f"{m['file']}:{m['line']}: {m['content']}"
                    for m in matches[:10]
                )
                self.console.print(
                    Panel(
                        match_str + (f"\n... and {total - 10} more" if total > 10 else ""),
                        title=f"✅ {tool_name} - {total} matches",
                        border_style="green"
                    )
                )
        elif tool_name == "glob":
            files = result.get("files", [])
            total = result.get("total", 0)
            if files:
                files_str = "\n".join(files[:20])
                self.console.print(
                    Panel(
                        files_str + (f"\n... and {total - 20} more" if total > 20 else ""),
                        title=f"✅ {tool_name} - {total} files",
                        border_style="green"
                    )
                )
        else:
            self.console.print(
                Panel(
                    json.dumps(result, indent=2)[:1000],
                    title=f"✅ {tool_name}",
                    border_style="green"
                )
            )

    def chat(self, user_message: str):
        """Simple chat interface without returning response."""
        self.run(user_message)

    def clear_history(self):
        """Clear conversation history."""
        self.conversation.clear()
        self.console.print("[yellow]Conversation history cleared[/yellow]")
