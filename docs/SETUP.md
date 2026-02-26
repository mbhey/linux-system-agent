# Setup Guide

## Prerequisites

1. **Python 3.10 or higher**
   ```bash
   python3 --version
   ```

2. **Ollama** - For running local LLMs
   - Install from: https://ollama.ai
   - Or: `curl -fsSL https://ollama.ai/install.sh | sh`

3. **System Requirements**
   - Kubuntu or Debian-based Linux distribution
   - sudo access for system modifications

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/linux-system-agent.git
cd linux-system-agent
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install langchain langchain-ollama langchain-community --break-system-packages
```

### 3. Install Optional Tools

For web search functionality:
```bash
sudo apt install ddgr
```

### 4. Configure Ollama

Ensure Ollama is running:
```bash
ollama serve
```

Pull a model (if not already available):
```bash
ollama pull qwen2:7b
```

### 5. Run the Agent

```bash
python3 linux_agent.py
```

## Configuration

### Custom Instructions

Custom instructions are stored in `~/.linux_agent/instructions.json`.

The agent automatically creates this file when you add instructions using:
- `add instruction <text>` - Add a custom instruction
- `list instructions` - Show all custom instructions
- `remove instruction <n>` - Remove by number
- `clear instructions` - Clear all

### Available Ollama Models

By default, the agent supports:
- `qwen2:7b` (default)
- `glm-4.7:cloud` (may require API key)

To use a different model, update the `AVAILABLE_MODELS` list in `linux_agent.py`.

## Troubleshooting

### Issue: "command not found: ollama"

Ensure Ollama is installed and in your PATH:
```bash
export PATH="$PATH:/usr/local/bin/ollama"
```

### Issue: LangChain Import Errors

Try upgrading langchain-core:
```bash
pip install --upgrade langchain-core --break-system-packages
```

### Issue: Permission Denied

Some commands require sudo. The agent will prompt for your password when needed.

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more solutions.
