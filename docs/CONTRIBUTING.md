# Contributing

Thank you for your interest in contributing to Linux System Agent!

## Ways to Contribute

### Reporting Bugs
- Use GitHub Issues to report bugs
- Include steps to reproduce and expected behavior
- Share your system details (OS, Python version, etc.)

### Suggesting Features
- Open a GitHub Issue with "Feature Request" label
- Describe the feature and its use case
- Explain why it would be beneficial

### Contributing Code

#### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/linux-system-agent.git
   cd linux-system-agent
   ```

3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### Adding New Tools

1. Add a new function with `@tool` decorator:
   ```python
   @tool
   def new_tool_name(param: str) -> str:
       """Description of what the tool does."""
       # Implementation
       return result
   ```

2. Add to `get_tools()` function list

3. Document in system prompt

4. Update FEATURES.md

#### Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions
- Keep functions focused and simple

#### Testing

Test your changes:
```bash
python3 linux_agent.py
```

Try various commands to ensure the agent works correctly.

#### Submitting Changes

1. Commit your changes:
   ```bash
   git add .
   git commit -m "Add new feature: feature_name"
   ```

2. Push to your fork:
   ```bash
   git push origin main
   ```

3. Create a Pull Request

## Guidelines

- Keep changes focused and atomic
- Test thoroughly before submitting
- Update documentation for any changes
- Be respectful in discussions

## Questions?

- Open an issue for general questions
- Check existing issues before creating new ones

Thank you for contributing!
