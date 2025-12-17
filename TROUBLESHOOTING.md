# Troubleshooting Guide

## Model Not Using Tools / Writing Code Instead of Editing Files

### Symptoms
- The AI shows you code in its response instead of actually modifying files
- You see HTML/CSS/JavaScript in the output but files don't change
- The model says "Here's the code:" followed by code blocks

### Solutions

#### 1. The CLI Now Auto-Corrects This!
The latest version automatically detects when the model outputs code instead of using tools and redirects it. You should see:
```
⚠️ Model generated code instead of using tools. Redirecting...
```

Then the model will be forced to use the actual tools.

#### 2. Use Non-Streaming Mode for Large Files
For complex modifications to large files, disable streaming:
```bash
aicli ask --no-stream "Make the products section responsive"
```

#### 3. Be More Explicit in Your Requests
Instead of:
```bash
# Less clear
aicli ask "make index.html responsive"
```

Try:
```bash
# More explicit
aicli ask "Read index.html, find the products section, and edit it to use CSS Grid with media queries for mobile"
```

#### 4. Use Better Models for Tool Calling

Some models are better at function calling than others:

**Best for tool calling:**
- `qwen2.5-coder:32b` ✅ Excellent
- `qwen2.5:32b` ✅ Excellent
- `llama3.1:70b` ✅ Very good (requires 40GB RAM)
- `llama3.3:70b` ✅ Very good (requires 40GB RAM)

**Good but sometimes needs redirection:**
- `qwen3-coder:30b` ⚠️ Good but occasionally outputs code
- `deepseek-r1:14b` ⚠️ Great reasoning but sometimes verbose

**Try to avoid for file editing:**
- `llama3.2:1b` ❌ Too small for reliable tool use
- Older models without tool calling support

To switch models:
```bash
# Pull a better model
ollama pull qwen2.5-coder:32b

# Use it
aicli -m qwen2.5-coder:32b ask "your request"
```

#### 5. Break Down Large Changes

For extensive modifications:
```bash
# Instead of: "Rewrite the entire website to be responsive"
# Do this:
aicli chat

> First, show me the structure of index.html
> Now make just the header section responsive
> Good! Now make the products section responsive
> Finally, update the footer
```

#### 6. Check the Actual File After

Always verify changes were made:
```bash
aicli ask "Add error handling to main.py"
cat main.py  # Check if it actually changed
```

## Common Issues

### Issue: "File not found"
**Solution:** Make sure you're in the right directory:
```bash
cd /path/to/your/project
aicli ask "your request"
```

Or specify the directory:
```bash
aicli -d /path/to/project ask "your request"
```

### Issue: Model is too slow
**Solution:** Use a smaller model:
```bash
ollama pull qwen2.5-coder:7b
aicli -m qwen2.5-coder:7b ask "your request"
```

### Issue: "edit_file: Old text not found"
This happens when the model tries to edit text that doesn't exactly match.

**Solution:** The model usually auto-recovers by:
1. Reading the file again
2. Using `write_file` instead to overwrite the whole file

If it keeps failing, try:
```bash
aicli ask "Read the file first, then rewrite the entire file with the changes"
```

### Issue: Changes are too aggressive
**Solution:** Be more conservative in your instructions:
```bash
# Instead of:
"Improve the code"

# Say:
"Only add error handling to the login function, don't change anything else"
```

## Debug Mode

Enable debug mode to see what's happening:
```bash
aicli ask --debug "your request"
```

This shows:
- All tool calls being made
- Parsed XML tool calls
- Why certain decisions were made

## Getting Help

If you're still having issues:

1. Check that Ollama is running: `ollama serve`
2. Verify your model supports tool calling: `ollama show <model-name>`
3. Try a different model known to work well
4. Use `--debug` flag to see what's happening
5. Share the debug output when asking for help

## Best Practices

1. ✅ **Always review changes** before committing to git
2. ✅ **Use chat mode** for multi-step tasks
3. ✅ **Be specific** about what to change
4. ✅ **Let the AI read files first** before making changes
5. ✅ **Use version control** so you can revert if needed
6. ❌ **Don't** ask for vague improvements
7. ❌ **Don't** modify files you haven't backed up
8. ❌ **Don't** run commands that could be destructive without reviewing

## Example Workflow

```bash
# Good workflow for making changes
aicli chat

> Read all the files in src/
> What does the authentication system look like?
> I want to add 2FA. What files would need to change?
> Start by reading auth.py
> Now add a verify_2fa function to auth.py
> Good! Now read the login route in routes.py
> Update the login route to use verify_2fa
> Perfect! Can you write a simple test for this?
> /quit

# Then review all changes
git diff

# Commit if good
git add .
git commit -m "Add 2FA support"
```
