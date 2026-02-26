# Usage Guide

## Running the Agent

```bash
python3 linux_agent.py
```

## Basic Examples

### Checking System Status

```
You: check for updates
You: show system info
You: detect hardware
You: show memory info
```

### Package Management

```
You: search for package firefox
You: install neofetch
You: remove vlc
You: add repository ppa:mozillateam/firefox-next
```

### System Maintenance

```
You: clean the system
You: tune performance
You: check disk usage
```

### File Operations

```
You: find files named document
You: delete /tmp/old_file.txt
You: reorganize my documents
You: create desktop icon for /usr/bin/htop named htop_top
```

### Process Management

```
You: list running processes
You: kill process 1234
You: restart nginx service
You: show all services
```

### Network

```
You: show network info
You: check firewall status
```

### Searching the Web

```
You: search for how to configure firewall
You: find best lightweight linux distros
```

### Custom Commands

```
You: run command ls -la
```

## Special Commands

### Switching Models

```
You: set model qwen2:7b
You: set model glm-4.7:cloud
```

### Managing Custom Instructions

```
You: add instruction prefer lightweight packages
You: list instructions
You: remove instruction 1
You: clear instructions
```

### Exiting

```
You: exit
```

## Output Formatting

The agent provides:
- **Green** "You:" for your input
- **Blue** "Agent:" for responses
- 1 blank line before response
- 3 blank lines after response

This makes it easy to distinguish between input and output.

## Tips

1. **Be Specific**: "install neofetch" is better than "install tool"
2. **Use Natural Language**: The agent understands plain English
3. **Check First**: Use "check for updates" before "upgrade system"
4. **Review Instructions**: Use "list instructions" to see your preferences

## Troubleshooting

If the agent doesn't understand:
- Try rephrasing your request
- Use more specific terms
- Check the tool is available in FEATURES.md

If commands fail:
- Some commands need sudo (agent will prompt)
- Check TROUBLESHOOTING.md for common issues
