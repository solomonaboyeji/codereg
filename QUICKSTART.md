# Quick Start Guide

## Installation (5 minutes)

### 1. Make sure Ollama is running

```bash
# Start Ollama (in a separate terminal)
ollama serve
```

### 2. Pull a recommended model

```bash
# Best for coding (requires ~20GB RAM)
ollama pull qwen3-coder:30b

# Or a smaller alternative
ollama pull qwen3-coder:7b
```

### 3. Install the CLI

```bash
# Install dependencies and CLI
python3 -m pip install -e .
```

### 4. Verify installation

```bash
aicli models
```

You should see your models listed.

## Your First Command

Try reading a file:

```bash
aicli ask "Read test_example.py and explain what it does"
```

## Interactive Mode

Start a conversation:

```bash
aicli chat
```

Then try these prompts:
- `Read all Python files and summarize the project structure`
- `Add type hints to the functions in test_example.py`
- `Create a new file called utils.py with helper functions for string manipulation`
- `Find all TODO comments in the codebase`

## Common Use Cases

### 1. Code Analysis
```bash
aicli ask "Analyze the code in src/ and identify potential bugs"
```

### 2. Add Features
```bash
aicli chat
> I want to add logging to all functions in main.py
```

### 3. Refactoring
```bash
aicli ask "Refactor the DatabaseConnection class to use context managers"
```

### 4. Generate Code
```bash
aicli ask "Create a new REST API endpoint for user registration in api.py"
```

### 5. Documentation
```bash
aicli ask "Add comprehensive docstrings to all functions in utils.py"
```

## Tips

1. **Let the AI explore**: Don't tell it exactly where files are - let it use glob/grep to find them
2. **Use chat mode for complex tasks**: Multi-step refactoring works better in interactive mode
3. **Review changes**: Always check what the AI modified before committing
4. **Start with analysis**: Ask it to read and understand before making changes

## Switching Models

Different models for different tasks:

```bash
# For complex reasoning
aicli -m deepseek-r1:14b chat

# For fast iterations
aicli -m llama3.2:1b ask "Find all Python files"

# For coding tasks (default)
aicli -m qwen3-coder:30b chat
```

## Troubleshooting

**Ollama connection error?**
```bash
# Make sure it's running
ollama serve
```

**Model not found?**
```bash
# Check available models
ollama list

# Pull if needed
ollama pull qwen3-coder:30b
```

**Tool calls not working?**
- Some models don't support function calling well
- Try qwen3-coder, qwen3, or llama3.1+ models

## Next Steps

1. Try it on your actual project
2. Experiment with different models
3. See README.md for advanced features
4. Report issues or contribute improvements!

## Example Session

```bash
$ aicli chat
> Read all the Python files in src/ and tell me about the architecture

[AI reads files and explains the structure]

> I want to add error handling to the database operations

[AI reads the database code, analyzes it, and adds try/except blocks]

> Now add logging for all database errors

[AI adds logging statements]

> Show me what you changed

[AI summarizes the modifications]

> /quit
```

Enjoy your local AI coding assistant!
