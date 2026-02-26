# Troubleshooting

## Common Issues

### Agent Won't Start

**Error**: `ModuleNotFoundError: No module named 'langchain'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Ollama Not Found

**Error**: `command not found: ollama`

**Solution**:
1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
2. Or add to PATH: `export PATH="$PATH:/usr/local/bin/ollama"`

### Model Not Available

**Error**: `model not found`

**Solution**:
```bash
ollama pull qwen2:7b
```

### Import Errors

**Error**: `cannot import name 'AgentExecutor' from 'langchain.agents'`

**Solution**:
```bash
pip install --upgrade langchain langchain-core --break-system-packages
```

### Permission Denied

**Error**: `Permission denied` when running commands

**Solution**: The agent will prompt for sudo when needed. Make sure you have sudo access.

### Web Search Not Working

**Error**: `Web search not available`

**Solution**:
```bash
sudo apt install ddgr
```

## Performance Issues

### Agent Response is Slow

- Try a smaller model: `set model qwen2:7b`
- Close other applications to free RAM
- Consider using a faster computer

### High CPU Usage

- Normal during agent thinking
- Check with `top` or `htop`

## Configuration Issues

### Custom Instructions Not Loading

Check the config file exists:
```bash
cat ~/.linux_agent/instructions.json
```

### Model Switching Not Working

Verify model is in AVAILABLE_MODELS list in `linux_agent.py`

## Getting Help

1. Check [FEATURES.md](FEATURES.md) for available tools
2. Review [USAGE.md](USAGE.md) for command examples
3. Check GitHub issues for similar problems

## Reporting Bugs

When reporting bugs, include:
- Your Linux distribution version
- Python version (`python3 --version`)
- Ollama version (`ollama --version`)
- The exact command that failed
- Error message received
