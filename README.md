# Linux System Agent

An AI-powered agent for managing Kubuntu/Linux systems using natural language commands.

## Features

- **Package Management**: Check updates, install/remove packages, search packages, add repositories
- **System Maintenance**: Clean system, tune performance, manage services
- **Hardware Info**: Detect hardware, CPU info, memory info, disk usage
- **File Operations**: Delete files, create desktop icons, reorganize documents, find files
- **Process Management**: List processes, kill processes, manage services
- **Network**: Show network connections and IP addresses
- **Custom Instructions**: Persistent user preferences that the agent always follows
- **Multiple LLM Support**: Switch between available Ollama models

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/linux-system-agent.git
cd linux-system-agent

# Install dependencies
pip install -r requirements.txt

# Run the agent
python3 linux_agent.py
```

## Requirements

- Python 3.10+
- Ollama (for local LLM)
- Kubuntu/Debian-based Linux distribution

See [SETUP.md](docs/SETUP.md) for detailed installation instructions.

## Usage

Run the agent and type commands:

```
You: check for updates
Agent: [checks and shows available updates]

You: install neofetch
Agent: [installs the package]

You: tune performance
Agent: [optimizes system settings]
```

### Available Commands

- `set model <model_name>` - Switch between available LLM models
- `add instruction <text>` - Add a custom instruction
- `list instructions` - Show all custom instructions
- `remove instruction <n>` - Remove instruction by number
- `clear instructions` - Remove all custom instructions
- `exit` - Quit the agent

See [USAGE.md](docs/USAGE.md) for more detailed usage examples.

## Documentation

- [SETUP.md](docs/SETUP.md) - Installation and configuration
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design and components
- [FEATURES.md](docs/FEATURES.md) - Complete feature list
- [ROADMAP.md](docs/ROADMAP.md) - Future development plans
- [CUSTOM_INSTRUCTIONS.md](docs/CUSTOM_INSTRUCTIONS.md) - How to configure persistent instructions

## License

MIT License - See [LICENSE](LICENSE) for details.
