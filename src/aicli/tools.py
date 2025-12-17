"""Tool system for file operations and code modifications."""

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
import glob as glob_module


class Tool:
    """Base class for tools."""

    name: str = ""
    description: str = ""

    def get_schema(self) -> Dict[str, Any]:
        """Return tool schema for function calling."""
        raise NotImplementedError

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        raise NotImplementedError


class ReadTool(Tool):
    """Read file contents."""

    name = "read_file"
    description = "Read the contents of a file"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The absolute or relative path to the file to read"
                        },
                        "start_line": {
                            "type": "integer",
                            "description": "Optional starting line number (1-indexed)"
                        },
                        "end_line": {
                            "type": "integer",
                            "description": "Optional ending line number (1-indexed)"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        }

    def execute(self, file_path: str, start_line: Optional[int] = None,
                end_line: Optional[int] = None) -> Dict[str, Any]:
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}"}

            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if start_line is not None or end_line is not None:
                start = (start_line - 1) if start_line else 0
                end = end_line if end_line else len(lines)
                lines = lines[start:end]

            # Add line numbers
            numbered_lines = [f"{i+1:6d}\t{line.rstrip()}"
                            for i, line in enumerate(lines)]

            return {
                "content": "\n".join(numbered_lines),
                "line_count": len(lines)
            }
        except Exception as e:
            return {"error": str(e)}


class WriteTool(Tool):
    """Write content to a file."""

    name = "write_file"
    description = "Write or overwrite a file with new content"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            }
        }

    def execute(self, file_path: str, content: str) -> Dict[str, Any]:
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {"success": True, "message": f"File written: {file_path}"}
        except Exception as e:
            return {"error": str(e)}


class EditTool(Tool):
    """Edit file by replacing text."""

    name = "edit_file"
    description = "Edit a file by replacing old text with new text"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to edit"
                        },
                        "old_text": {
                            "type": "string",
                            "description": "The exact text to replace"
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The new text to insert"
                        }
                    },
                    "required": ["file_path", "old_text", "new_text"]
                }
            }
        }

    def execute(self, file_path: str, old_text: str, new_text: str) -> Dict[str, Any]:
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}"}

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            if old_text not in content:
                return {"error": "Old text not found in file"}

            # Check if old_text appears multiple times
            count = content.count(old_text)
            if count > 1:
                return {"error": f"Old text appears {count} times in file. Please be more specific."}

            new_content = content.replace(old_text, new_text, 1)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return {"success": True, "message": f"File edited: {file_path}"}
        except Exception as e:
            return {"error": str(e)}


class GrepTool(Tool):
    """Search for patterns in files."""

    name = "grep"
    description = "Search for a pattern in files using regex"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "The regex pattern to search for"
                        },
                        "path": {
                            "type": "string",
                            "description": "The file or directory to search in (default: current directory)"
                        },
                        "file_pattern": {
                            "type": "string",
                            "description": "File pattern to filter (e.g., '*.py', '*.js')"
                        }
                    },
                    "required": ["pattern"]
                }
            }
        }

    def execute(self, pattern: str, path: str = ".",
                file_pattern: str = "*") -> Dict[str, Any]:
        try:
            matches = []
            search_path = Path(path)

            if search_path.is_file():
                files = [search_path]
            else:
                # Find all matching files
                files = list(search_path.rglob(file_pattern))

            regex = re.compile(pattern)

            for file in files:
                if file.is_file():
                    try:
                        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                if regex.search(line):
                                    matches.append({
                                        "file": str(file),
                                        "line": line_num,
                                        "content": line.rstrip()
                                    })
                    except:
                        continue

            return {
                "matches": matches[:100],  # Limit results
                "total": len(matches)
            }
        except Exception as e:
            return {"error": str(e)}


class GlobTool(Tool):
    """Find files matching a pattern."""

    name = "glob"
    description = "Find files matching a glob pattern"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "The glob pattern (e.g., '**/*.py', 'src/**/*.js')"
                        },
                        "path": {
                            "type": "string",
                            "description": "The directory to search in (default: current directory)"
                        }
                    },
                    "required": ["pattern"]
                }
            }
        }

    def execute(self, pattern: str, path: str = ".") -> Dict[str, Any]:
        try:
            search_path = Path(path)
            files = list(search_path.glob(pattern))

            # Sort by modification time, newest first
            files.sort(key=lambda x: x.stat().st_mtime if x.exists() else 0, reverse=True)

            return {
                "files": [str(f) for f in files[:100]],  # Limit results
                "total": len(files)
            }
        except Exception as e:
            return {"error": str(e)}


class BashTool(Tool):
    """Execute bash commands."""

    name = "bash"
    description = "Execute a bash command and return output"

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute"
                        }
                    },
                    "required": ["command"]
                }
            }
        }

    def execute(self, command: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out after 30 seconds"}
        except Exception as e:
            return {"error": str(e)}


class ToolRegistry:
    """Registry of all available tools."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {
            "read_file": ReadTool(),
            "write_file": WriteTool(),
            "edit_file": EditTool(),
            "grep": GrepTool(),
            "glob": GlobTool(),
            "bash": BashTool(),
        }

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        return [tool.get_schema() for tool in self.tools.values()]

    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Unknown tool: {name}"}
        return tool.execute(**kwargs)
