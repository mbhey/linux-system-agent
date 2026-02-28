# Features

## Current Features

### Package Management

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| Check Updates | Check for available package updates | `check for updates` |
| Upgrade System | Upgrade all system packages | `upgrade the system` |
| Install Package | Install a package | `install neofetch` |
| Remove Package | Remove an installed package | `remove vlc` |
| Search Package | Search for packages in repos | `search for package vim` |
| Add Repository | Add PPA or custom repository | `add repository ppa:mozillateam/firefox-next` |

### System Maintenance

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| Clean System | Clean package cache and temp files | `clean the system` |
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
| Firewall Status | Check firewall status | `check firewall` |

### Network

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| Network Info | Show IP and connections | `show network info` |

### Web Search & Diagnostics (NEW!)

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| Search Web | Search the internet (English/Arabic) | `search for ubuntu tips` |
| Fetch URL | Fetch and parse web page content | `fetch https://wiki.archlinux.org` |
| Search Docs | Search Linux documentation | `search documentation nvidia` |
| Diagnose Error | Diagnose errors and find solutions | `diagnose error "package not found"` |

### Auto-Fix System (NEW!)

When commands fail, the agent automatically:
1. Detects error type (package, service, network, permission, disk)
2. Provides suggested fixes
3. Searches online for solutions

This works automatically for:
- `install_package` - Package installation errors
- `upgrade_system` - System upgrade errors  
- `system_services` - Service management errors

### Utilities

| Feature | Description | Command Example |
|---------|-------------|-----------------|
| Run Command | Execute shell command | `run command ls -la` |

## Special Commands

| Command | Description |
|---------|-------------|
| `set model <name>` | Switch to a different LLM model |
| `set search limit <n>` | Set searches per minute (1-20) |
| `set language <en\|ar>` | Set search language |
| `show config` | Display current settings |
| `add instruction <text>` | Add a persistent custom instruction |
| `list instructions` | Show all custom instructions |
| `remove instruction <n>` | Remove a custom instruction by number |
| `clear instructions` | Remove all custom instructions |
| `exit` | Quit the agent |

## Configuration

The agent has configurable settings:

- **Search rate limit**: 5/minute (configurable 1-20)
- **Search language**: English (en) or Arabic (ar)
- **Auto-fix**: Enabled by default

View settings: `show config`

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

## Cross-Distribution Support

Works on multiple Linux distributions:
- Ubuntu/Debian (apt)
- Fedora/RHEL (dnf/yum)
- Arch/Manjaro (pacman)
- openSUSE (zypper)
- Alpine (apk)
