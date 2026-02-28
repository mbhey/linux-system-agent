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
   - Any Linux distribution (Ubuntu, Fedora, Arch, openSUSE, etc.)
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

The dependencies include:
- `langchain` - Agent framework
- `langchain-ollama` - Ollama LLM integration
- `langchain-community` - Additional utilities
- `langgraph` - Agent execution graph
- `duckduckgo-search` - Web search (Python-based)
- `beautifulsoup4` - HTML parsing for URL fetching
- `requests` - HTTP requests
- `lxml` - Fast XML/HTML parsing

### 3. Configure Ollama

Ensure Ollama is running:
```bash
ollama serve
```

Pull a model (if not already available):
```bash
ollama pull qwen2:7b
```

### 4. Run the Agent

```bash
python3 linux_agent.py
```

Or use the setup script for full installation with desktop entry:

```bash
chmod +x setup.sh
./setup.sh
```

## Configuration

### Custom Instructions

Custom instructions are stored in `~/.linux_agent/instructions.json`.

Commands:
- `add instruction <text>` - Add a custom instruction
- `list instructions` - Show all custom instructions
- `remove instruction <n>` - Remove by number
- `clear instructions` - Clear all

### Search Configuration

- **Rate limit**: Default 5 searches/minute (configurable 1-20)
- **Language**: Default English (can set to Arabic)
- **Commands**:
  - `set search limit <n>` - Change rate limit
  - `set language <en|ar>` - Change language
  - `show config` - Display all settings

### Available Ollama Models

By default, the agent supports:
- `qwen2:7b` (default)
- `glm-4.7:cloud` (may require API key)

To use a different model:
```
set model qwen2:7b
```

## Cross-Distribution Support

The agent automatically detects your Linux distribution and uses the appropriate package manager:

| Distribution | Package Manager |
|--------------|-----------------|
| Ubuntu/Debian | apt |
| Fedora/RHEL | dnf/yum |
| Arch/Manjaro | pacman |
| openSUSE | zypper |
| Alpine | apk |

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

### Issue: Web Search Not Working

Make sure dependencies are installed:
```bash
pip install duckduckgo-search beautifulsoup4 requests lxml
```

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more solutions.
