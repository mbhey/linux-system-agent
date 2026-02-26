# Custom Instructions

Custom instructions allow you to define persistent preferences that the agent will always follow. These are stored locally and loaded every time the agent starts.

## How It Works

1. You add instructions using the `add instruction` command
2. Instructions are saved to `~/.linux_agent/instructions.json`
3. On each agent start, instructions are loaded and prepended to the system prompt
4. The agent follows these instructions for every response

## Managing Instructions

### Add an Instruction

```
You: add instruction prefer lightweight packages
Agent: Instruction added. Total: 1
```

### List All Instructions

```
You: list instructions
Agent: Custom instructions:
1. prefer lightweight packages
```

### Remove an Instruction

```
You: remove instruction 1
Agent: Removed: prefer lightweight packages
```

### Clear All Instructions

```
You: clear instructions
Agent: All instructions cleared.
```

## Example Instructions

Here are useful custom instructions you can add:

### Package Management
```
prefer flatpak over apt when available
always suggest snap packages for GUI applications
never install packages without showing what will be installed first
```

### Safety
```
always confirm before running sudo commands
explain what each command will do before executing it
never delete files without confirmation
create backup before modifying system files
```

### Behavior
```
respond in short concise sentences
use bullet points for lists
show command output when relevant
```

### Performance
```
prioritize system responsiveness over power saving
suggest performance optimizations for my hardware
```

## Configuration File

Instructions are stored in JSON format:

```json
{
  "instructions": [
    "prefer lightweight packages",
    "always confirm before running sudo commands"
  ]
}
```

Location: `~/.linux_agent/instructions.json`

## Tips

- Keep instructions short and clear
- Avoid contradictory instructions
- Review and update instructions periodically
- Use `list instructions` to verify current settings
