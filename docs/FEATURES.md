# Features

## Current Features

### Package Management

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| Check Updates | Check for available package updates | `check for updates` |
| Upgrade System | Upgrade all system packages | `upgrade the system` |
| Install Package | Install a package via apt | `install neofetch` |
| Remove Package | Remove an installed package | `remove vlc` |
| Search Package | Search for packages in repos | `search for package vim` |
| Add Repository | Add PPA or custom repository | `add repository ppa:mozillateam/firefox-next` |

### System Maintenance

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| Clean System | Clean apt cache and temp files | `clean the system` |
| Tune Performance | Optimize system for hardware | `tune performance` |
| System Info | Show detailed system information | `show system info` |
| CPU Info | Show CPU details | `show cpu info` |
| Memory Info | Show memory usage | `show memory info` |
| Detect Hardware | Detect hardware components | `detect hardware` |

### File Operations

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| Delete Path | Delete file or folder | `delete /tmp/test.txt` |
| Create Desktop Icon | Create .desktop launcher | `create desktop icon for /usr/bin/htop named htop` |
| Reorganize Documents | Organize ~/Documents by type | `reorganize my documents` |
| Find Files | Search for files by name | `find files named test` |
| Directory Size | Show directory sizes | `show largest directories` |
| Disk Usage | Show disk space | `check disk usage` |

### Process & Service Management

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| List Processes | Show running processes | `list processes` |
| Kill Process | Terminate a process | `kill process 1234` |
| Manage Services | Start/stop/restart services | `restart nginx` |
| List Services | Show all services | `list services` |
| Firewall Status | Check UFW firewall status | `check firewall` |

### Network

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| Network Info | Show IP and connections | `show network info` |

### Utilities

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| Search Web | Search the internet | `search for latest ubuntu tips` |
| Run Command | Execute shell command | `run command ls -la` |

## Special Commands

| Command | Description |
|---------|-------------|
| `set model <name>` | Switch to a different LLM model |
| `add instruction <text>` | Add a persistent custom instruction |
| `list instructions` | Show all custom instructions |
| `remove instruction <n>` | Remove a custom instruction by number |
| `clear instructions` | Remove all custom instructions |
| `exit` | Quit the agent |

## Custom Instructions

The agent supports persistent custom instructions that are always followed.

Example instructions:
- "Prefer lightweight packages over heavy ones"
- "Always confirm before running sudo commands"
- "Explain what you're doing before doing it"

See [CUSTOM_INSTRUCTIONS.md](CUSTOM_INSTRUCTIONS.md) for details.

## Model Support

- **qwen2:7b** - Default, good balance of speed and capability
- **glm-4.7:cloud** - May require API key

Switch models with: `set model qwen2:7b`
