# Architecture

## Overview

Linux System Agent is built using LangChain and LangGraph, leveraging local LLMs through Ollama for natural language understanding and tool execution.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│         (Terminal - Colored CLI Output)                  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                    Agent Core                            │
│         (LangGraph create_react_agent)                  │
│         - Reasoning & Decision Making                   │
│         - Tool Selection & Execution                     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│                     Tool Layer                           │
├─────────────────────────────────────────────────────────┤
│  Package    │  System   │  File    │  Network │  Search │
│  Manager   │  Admin    │  Ops     │  Info    │  Web    │
└────────────┴───────────┴──────────┴─────────┴──────────┘
                      │
┌─────────────────────┴───────────────────────────────────┐
│              Linux System (Kubuntu)                     │
│    apt, systemctl, files, processes, network, etc.      │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Agent Core (`linux_agent.py`)

- **LLM Integration**: Uses ChatOllama to connect with local LLM models
- **System Prompt**: Defines agent behavior and available tools
- **Tool Registry**: 26+ tools for various system operations
- **Instruction Handler**: Manages persistent user preferences

### 2. Tool Layer

All tools are implemented as LangChain `@tool` decorated functions:

| Category | Tools |
|----------|-------|
| **Updates & Packages** | check_updates, upgrade_system, install_package, remove_package, search_package, add_repository |
| **System & Hardware** | detect_hardware, tune_performance, system_info, cpu_info, memory_info |
| **Files & Storage** | disk_usage, directory_size, delete_path, find_files, create_desktop_icon, reorganize_documents |
| **Processes & Services** | list_processes, kill_process, system_services, list_services |
| **Network** | network_info, firewall_status |
| **Utilities** | search_web, run_command |

### 3. Configuration

- **Config Directory**: `~/.linux_agent/`
- **Instructions File**: `~/.linux_agent/instructions.json`
- **Format**: JSON with "instructions" array

### 4. User Interface

- **Colored Output**: Green for user input, Blue for agent response
- **Command Parser**: Handles special commands (set model, add instruction, etc.)
- **Error Handling**: Graceful error messages

## Data Flow

1. **User Input** → Colored CLI receives natural language command
2. **LLM Reasoning** → Agent analyzes request and selects appropriate tool(s)
3. **Tool Execution** → Selected tool(s) execute on Linux system
4. **Result Processing** → Tool output is formatted and returned to user

## Key Design Decisions

1. **Local LLM**: Uses Ollama for privacy and offline capability
2. **ReAct Agent**: Uses ReAct (Reasoning + Acting) pattern for tool use
3. **Simple Config**: JSON file for custom instructions (no database needed)
4. **Safety First**: Confirmation prompts for destructive operations

## Extending the Agent

To add new tools:

1. Add a new `@tool` decorated function in `linux_agent.py`
2. Include it in the `get_tools()` function list
3. Document it in the system prompt
4. Add to FEATURES.md

## Dependencies

- `langchain` - Agent framework
- `langchain-ollama` - Ollama LLM integration
- `langchain-community` - Additional utilities
- `langgraph` - Agent execution graph
