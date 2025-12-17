# AI CLI

A Claude Code-like CLI tool that uses local Ollama models to read, understand, and modify code projects. Save money by using free, local AI models instead of cloud APIs!

> **NEW:** Auto-detection and correction when models output code instead of using tools! The CLI now automatically catches when the AI tries to show you code instead of editing files, and redirects it to use the proper tools. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for details.

## Features

- 🤖 **Tool Calling Support**: The AI can read files, edit code, search patterns, and execute bash commands
- 💬 **Interactive Chat Mode**: Have a conversation with the AI about your code
- 📁 **File Operations**: Read, write, edit files with intelligent context awareness
- 🔍 **Code Search**: Use grep and glob to find files and patterns
- 🛠️ **Bash Execution**: Run commands to test, build, or analyze your project
- 💰 **Cost-Free**: Uses local Ollama models - no API costs!
- 🔄 **Auto-Correction**: Detects and redirects when models output code instead of using tools
- 🐛 **Debug Mode**: See exactly what's happening under the hood

## Installation

### Prerequisites

1. **Install Ollama** (if not already installed):
   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Start Ollama**:
   ```bash
   ollama serve
   ```

3. **Pull a model** (recommended models for coding):
   ```bash
   # Best for coding (if you have 20GB+ RAM)
   ollama pull qwen3-coder:30b

   # Good alternatives
   ollama pull qwen3:30b
   ollama pull deepseek-r1:14b
   ollama pull codellama:34b
   ```

### Install AI CLI

```bash
# Install in development mode
pip install -e .

# Or install dependencies separately
pip install click requests rich prompt-toolkit
```

## Usage

### Quick Start

```bash
# Show help
aicli

# List available models
aicli models

# Ask a single question
aicli ask "Read src/main.py and explain what it does"

# Start interactive chat
aicli chat
```

### Interactive Mode

The chat mode allows you to have a continuous conversation with the AI:

```bash
aicli chat
```

Commands in chat mode:
- `/clear` - Clear conversation history
- `/quit` - Exit chat mode
- `Ctrl+C` - Exit chat mode

### Examples

**Read and analyze code:**
```bash
aicli ask "Read all Python files and tell me about the architecture"
```

**Make changes:**
```bash
aicli ask "Add error handling to the API endpoints in src/api.py"
```

**Search and refactor:**
```bash
aicli ask "Find all uses of the old authentication method and update them to use the new one"
```

**Create new features:**
```bash
aicli chat
> I want to add a logging system to the project. Can you help?
```

### Options

```bash
aicli --help

Options:
  -m, --model TEXT         Ollama model to use (default: qwen3-coder:30b)
  -u, --url TEXT          Ollama API URL (default: http://localhost:11434)
  -d, --project-dir TEXT  Project directory (default: current directory)
  --debug                 Enable debug output to see tool calls
  --no-stream             Disable streaming (better for large file edits)
```

**Use a different model:**
```bash
aicli -m deepseek-r1:14b ask "Optimize the database queries in models.py"
```

**Work in a different directory:**
```bash
aicli -d /path/to/project chat
```

**Debug mode (see what's happening):**
```bash
aicli ask --debug "Add logging to main.py"
```

**For large file modifications:**
```bash
aicli ask --no-stream "Rewrite the entire products section in index.html to be responsive"
```

## Available Tools

The AI has access to these tools:

| Tool | Description |
|------|-------------|
| `read_file` | Read file contents with optional line ranges |
| `write_file` | Create or overwrite files |
| `edit_file` | Edit files by replacing specific text |
| `grep` | Search for patterns in files using regex |
| `glob` | Find files matching glob patterns (e.g., `**/*.py`) |
| `bash` | Execute bash commands (30s timeout) |

## Model Recommendations

**Best models for file editing (strong tool calling):**

1. **qwen2.5-coder:32b** ⭐ - Latest, best for coding with excellent tool use (~20GB RAM)
2. **qwen2.5:32b** ⭐ - Excellent general purpose with reliable tool calling (~20GB RAM)
3. **llama3.3:70b** - Very capable but requires significant RAM (~40GB)
4. **llama3.1:70b** - Excellent but requires significant RAM (~40GB)
5. **devstral-small-2:latest** - Built the mass calulator in this project

**Good models (may need auto-correction):**

5. **qwen3-coder:30b** ⚠️ - Good for coding, occasionally outputs code instead of using tools (~20GB RAM)
6. **deepseek-r1:14b** ⚠️ - Great reasoning but sometimes needs redirection (~10GB RAM)
7. **qwen3:30b** ⚠️ - Good general-purpose, decent tool calling (~20GB RAM)

**Smaller/faster models:**
- **qwen2.5-coder:7b** - Faster, good for simple tasks (~4GB RAM)
- **qwen3-coder:7b** - Decent for basic edits (~4GB RAM)
- **llama3.2:1b** ❌ - Too small for reliable file editing (~1GB RAM)

> **Note:** Models marked with ⭐ have the most reliable tool calling. Models with ⚠️ work but the CLI's auto-correction will occasionally redirect them. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for details.

## How It Works

1. You provide instructions to the AI
2. The AI analyzes your request and decides which tools to use
3. Tools are executed (read files, search code, etc.)
4. The AI processes the results and may call more tools
5. The AI provides a response and/or makes modifications
6. The conversation continues until the task is complete

## Tips for Best Results

- **Be specific**: "Add error handling to the login function in auth.py" works better than "improve the code"
- **Provide context**: The AI can read files, so let it explore the codebase first
- **Use chat mode for complex tasks**: Multi-step refactoring works better in interactive mode
- **Check changes**: Always review the AI's modifications before committing
- **Start small**: Test with simple tasks to understand the AI's capabilities

## Troubleshooting

### Model Not Making Changes to Files

If the AI shows you code instead of actually modifying files:

1. **Auto-correction should kick in** - You'll see a yellow warning and the model will be redirected
2. **Try `--no-stream` mode** for large file edits: `aicli ask --no-stream "your request"`
3. **Use a better model** like `qwen2.5-coder:32b` or `llama3.3:70b`
4. **See the full guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Common Issues

**"Model not found" error:**
```bash
ollama list              # List available models
ollama pull qwen2.5-coder:32b  # Pull a recommended model
```

**"Error connecting to Ollama":**
```bash
ollama serve  # Make sure Ollama is running
```

**Out of memory:**
```bash
ollama pull qwen2.5-coder:7b  # Use a smaller model
```

**Need more help?**
- See detailed guide: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Use `--debug` flag to see what's happening
- Check model compatibility in the Model Recommendations section above

## Comparison with Claude Code

| Feature | AI CLI | Claude Code |
|---------|--------|-------------|
| Cost | Free (local) | $20+/month |
| Speed | Depends on hardware | Fast (cloud) |
| Privacy | 100% local | Cloud-based |
| Models | Any Ollama model | Claude only |
| Tool calling | ✅ | ✅ |
| Context size | Model dependent | Very large |
| Offline use | ✅ | ❌ |

## Contributing

This is a basic implementation. Contributions welcome for:
- Better error handling
- More tools (git operations, testing, etc.)
- Streaming improvements
- Context management enhancements
- Model-specific optimizations

## License

MIT
