#!/usr/bin/env python3
"""
Linux System Agent - An AI agent for Linux system management
Supports: Ubuntu, Debian, Fedora, Arch, openSUSE, and derivatives
"""

import subprocess
import os
import shutil
import json
import platform
from pathlib import Path
from typing import Optional, List

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


AVAILABLE_MODELS = ["qwen2:7b", "glm-4.7:cloud"]
DEFAULT_MODEL = "qwen2:7b"

CONFIG_DIR = Path.home() / ".linux_agent"
CONFIG_FILE = CONFIG_DIR / "instructions.json"


class LinuxDistro:
    """Detects and manages Linux distribution-specific commands."""

    def __init__(self):
        self.distro = self.detect_distro()
        self.package_manager = self.get_package_manager()
        self.service_manager = "systemctl"

    def detect_distro(self) -> str:
        """Detect the Linux distribution."""
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            return line.split("=")[1].strip().strip('"')
        except:
            pass
        return "unknown"

    def get_package_manager(self) -> dict:
        """Get package manager commands based on distro."""
        pkg_managers = {
            "ubuntu": {
                "name": "apt",
                "update": "apt update",
                "upgrade": "DEBIAN_FRONTEND=noninteractive sudo apt upgrade -y",
                "install": "DEBIAN_FRONTEND=noninteractive sudo apt install -y",
                "remove": "sudo apt remove -y",
                "search": "apt search",
                "autoremove": "sudo apt autoremove -y",
                "clean": "sudo apt clean",
            },
            "debian": {
                "name": "apt",
                "update": "apt update",
                "upgrade": "DEBIAN_FRONTEND=noninteractive sudo apt upgrade -y",
                "install": "DEBIAN_FRONTEND=noninteractive sudo apt install -y",
                "remove": "sudo apt remove -y",
                "search": "apt search",
                "autoremove": "sudo apt autoremove -y",
                "clean": "sudo apt clean",
            },
            "fedora": {
                "name": "dnf",
                "update": "sudo dnf check-update",
                "upgrade": "sudo dnf upgrade -y",
                "install": "sudo dnf install -y",
                "remove": "sudo dnf remove -y",
                "search": "dnf search",
                "autoremove": "sudo dnf autoremove -y",
                "clean": "sudo dnf clean all",
            },
            "rhel": {
                "name": "dnf",
                "update": "sudo dnf check-update",
                "upgrade": "sudo dnf upgrade -y",
                "install": "sudo dnf install -y",
                "remove": "sudo dnf remove -y",
                "search": "dnf search",
                "autoremove": "sudo dnf autoremove -y",
                "clean": "sudo dnf clean all",
            },
            "centos": {
                "name": "yum",
                "update": "sudo yum check-update",
                "upgrade": "sudo yum update -y",
                "install": "sudo yum install -y",
                "remove": "sudo yum remove -y",
                "search": "yum search",
                "autoremove": "sudo yum autoremove -y",
                "clean": "sudo yum clean all",
            },
            "arch": {
                "name": "pacman",
                "update": "sudo pacman -Sy",
                "upgrade": "sudo pacman -Syu",
                "install": "sudo pacman -S --noconfirm",
                "remove": "sudo pacman -R --noconfirm",
                "search": "pacman -Ss",
                "autoremove": "sudo pacman -Rcs --noconfirm",
                "clean": "sudo pacman -Scc --noconfirm",
            },
            "manjaro": {
                "name": "pacman",
                "update": "sudo pacman -Sy",
                "upgrade": "sudo pacman -Syu",
                "install": "sudo pacman -S --noconfirm",
                "remove": "sudo pacman -R --noconfirm",
                "search": "pacman -Ss",
                "autoremove": "sudo pacman -Rcs --noconfirm",
                "clean": "sudo pacman -Scc --noconfirm",
            },
            "opensuse": {
                "name": "zypper",
                "update": "sudo zypper refresh",
                "upgrade": "sudo zypper update -y",
                "install": "sudo zypper install -y",
                "remove": "sudo zypper remove -y",
                "search": "zypper search",
                "autoremove": "sudo zypper remove --clean-deps -y",
                "clean": "sudo zypper clean --all",
            },
            "alpine": {
                "name": "apk",
                "update": "sudo apk update",
                "upgrade": "sudo apk upgrade",
                "install": "sudo apk add",
                "remove": "sudo apk del",
                "search": "apk search",
                "autoremove": "sudo apk cache clean",
                "clean": "sudo apk cache clean",
            },
        }

        # Check for known derivatives
        distro_lower = self.distro.lower()

        # Check for Ubuntu/Debian derivatives
        if distro_lower in ["ubuntu", "debian", "linuxmint", "pop"]:
            return pkg_managers["ubuntu"]
        # Check for Fedora/RHEL derivatives
        elif distro_lower in ["fedora", "rhel", "centos", "rocky", "alma"]:
            return pkg_managers.get(distro_lower, pkg_managers["fedora"])
        # Check for Arch derivatives
        elif distro_lower in ["arch", "manjaro", "endeavouros"]:
            return pkg_managers.get(distro_lower, pkg_managers["arch"])
        # Check for openSUSE
        elif distro_lower in ["opensuse", "sles"]:
            return pkg_managers["opensuse"]
        # Default to apt
        else:
            return pkg_managers["ubuntu"]

    def get_upgrade_command(self) -> str:
        return self.package_manager["upgrade"]

    def get_install_command(self, package: str) -> str:
        return f"{self.package_manager['install']} {package}"

    def get_remove_command(self, package: str) -> str:
        return f"{self.package_manager['remove']} {package}"

    def get_update_command(self) -> str:
        return self.package_manager["update"]

    def get_clean_command(self) -> str:
        return self.package_manager["clean"]

    def get_autoremove_command(self) -> str:
        return self.package_manager["autoremove"]

    def get_search_command(self, package: str) -> str:
        return f"{self.package_manager['search']} {package}"


# Global distro instance
distro = LinuxDistro()


def ensure_config_dir():
    """Ensure config directory exists."""
    CONFIG_DIR.mkdir(exist_ok=True)


def load_instructions() -> List[str]:
    """Load custom instructions from config file."""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("instructions", [])
        except:
            return []
    return []


def save_instructions(instructions: List[str]) -> None:
    """Save custom instructions to config file."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump({"instructions": instructions}, f, indent=2)


def format_custom_instructions() -> str:
    """Format custom instructions for the system prompt."""
    instructions = load_instructions()
    if not instructions:
        return ""

    formatted = "\n\nUSER PREFERENCES (always follow these):\n"
    for i, instr in enumerate(instructions, 1):
        formatted += f"- {instr}\n"
    return formatted


@tool
def check_updates() -> str:
    """Check for system and package updates."""
    result = subprocess.run(
        f"{distro.get_update_command()} 2>&1",
        shell=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr

    # Get upgradable packages (different for each distro)
    if distro.package_manager["name"] in ["apt"]:
        result2 = subprocess.run(
            "apt list --upgradable 2>/dev/null",
            shell=True,
            capture_output=True,
            text=True,
        )
        output += "\n" + result2.stdout
    elif distro.package_manager["name"] in ["dnf", "yum"]:
        result2 = subprocess.run(
            "dnf list updates 2>&1", shell=True, capture_output=True, text=True
        )
        output += "\n" + result2.stdout
    elif distro.package_manager["name"] == "pacman":
        result2 = subprocess.run(
            "pacman -Qu 2>&1", shell=True, capture_output=True, text=True
        )
        output += "\n" + result2.stdout
    elif distro.package_manager["name"] == "zypper":
        result2 = subprocess.run(
            "zypper list-updates 2>&1", shell=True, capture_output=True, text=True
        )
        output += "\n" + result2.stdout

    return output


@tool
def upgrade_system() -> str:
    """Upgrade all system packages."""
    result = subprocess.run(
        f"{distro.get_upgrade_command()} 2>&1",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


@tool
def clean_system() -> str:
    """Clean system from temp files, cache, and old packages."""
    results = []

    cmds = [
        (f"Clean {distro.package_manager['name']} cache", distro.get_clean_command()),
        ("Remove auto-remove", distro.get_autoremove_command()),
    ]

    for name, cmd in cmds:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        results.append(f"{name}: {'OK' if result.returncode == 0 else 'Failed'}")

    return "\n".join(results)


@tool
def detect_hardware() -> str:
    """Detect system hardware for tuning."""
    cpu_info = subprocess.run(
        "lscpu | grep 'Model name' | cut -d: -f2",
        shell=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    mem_info = subprocess.run(
        "free -h", shell=True, capture_output=True, text=True
    ).stdout
    disk_info = subprocess.run(
        "lsblk -d -o NAME,SIZE,TYPE | grep disk",
        shell=True,
        capture_output=True,
        text=True,
    ).stdout

    return f"CPU: {cpu_info}\n\nMemory:\n{mem_info}\nDisk:\n{disk_info}"


@tool
def tune_performance() -> str:
    """Tune system for best performance based on hardware."""
    cpu_info = subprocess.run(
        "lscpu | grep 'Model name' | cut -d: -f2",
        shell=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    results = [f"=== Applying Performance Tunings ===\nDetected CPU: {cpu_info}"]

    result = subprocess.run(
        "echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null",
        shell=True,
        capture_output=True,
        text=True,
    )
    results.append(
        f"CPU governor -> performance: {'OK' if result.returncode == 0 else 'Partial'}"
    )

    result = subprocess.run(
        "sudo sysctl -w vm.swappiness=10 2>&1",
        shell=True,
        capture_output=True,
        text=True,
    )
    results.append(f"Swappiness -> 10: {'OK' if result.returncode == 0 else 'Failed'}")

    return "\n".join(results)


@tool
def install_package(package_name: str) -> str:
    """Install a package by name."""
    result = subprocess.run(
        f"{distro.get_install_command(package_name)} 2>&1",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


@tool
def remove_package(package_name: str) -> str:
    """Remove/uninstall a package by name."""
    result = subprocess.run(
        f"{distro.get_remove_command(package_name)} 2>&1",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


@tool
def search_package(package_name: str) -> str:
    """Search for a package in repositories."""
    result = subprocess.run(
        f"{distro.get_search_command(package_name)} 2>&1 | head -20",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


@tool
def add_repository(repo_line: str) -> str:
    """Add a repository (e.g., ppa:user/repo or deb line)."""
    result = subprocess.run(
        f"sudo add-apt-repository -y {repo_line} 2>&1",
        shell=True,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return f"Failed: {result.stderr}"

    subprocess.run("sudo apt update 2>&1", shell=True)
    return f"Repository added: {repo_line}"


@tool
def delete_path(path: str) -> str:
    """Delete a file or folder at the given path."""
    if not os.path.exists(path):
        return f"Path does not exist: {path}"

    try:
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
        return f"Deleted: {path}"
    except Exception as e:
        return f"Error deleting {path}: {e}"


@tool
def create_desktop_icon(
    name: str, exec_path: str, icon_path: Optional[str] = None, terminal: bool = False
) -> str:
    """Create a .desktop file for an application."""
    desktop_dir = Path.home() / ".local" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)

    desktop_file = desktop_dir / f"{name.lower().replace(' ', '_')}.desktop"

    content = f"""[Desktop Entry]
Type=Application
Name={name}
Exec={exec_path}
"""
    if icon_path:
        content += f"Icon={icon_path}\n"
    content += f"Terminal={'true' if terminal else 'false'}\n"
    content += "Categories=Utility;\n"

    desktop_file.write_text(content)
    desktop_file.chmod(0o755)

    return f"Desktop icon created at: {desktop_file}"


@tool
def reorganize_documents() -> str:
    """Organize files in ~/Documents by type/category."""
    docs = Path.home() / "Documents"
    if not docs.exists():
        return "Documents folder not found"

    categories = {
        "Images": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf"],
        "Spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
        "Presentations": [".ppt", ".pptx", ".odp"],
        "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
        "Code": [".py", ".js", ".java", ".cpp", ".c", ".h", ".sh", ".go", ".rs"],
    }

    moved = []
    for category, extensions in categories.items():
        cat_dir = docs / category
        cat_dir.mkdir(exist_ok=True)

        for ext in extensions:
            for f in docs.glob(f"*{ext}"):
                if f.is_file() and f.parent == docs:
                    dest = cat_dir / f.name
                    f.rename(dest)
                    moved.append(f"{f.name} -> {category}/")

    if moved:
        return "Reorganized:\n" + "\n".join(moved)
    return "No files to reorganize"


@tool
def list_processes() -> str:
    """List running processes."""
    result = subprocess.run(
        "ps aux --sort=-%cpu | head -20", shell=True, capture_output=True, text=True
    )
    return result.stdout


@tool
def kill_process(pid: str) -> str:
    """Kill a process by PID."""
    result = subprocess.run(
        f"sudo kill {pid} 2>&1", shell=True, capture_output=True, text=True
    )
    if result.returncode == 0:
        return f"Process {pid} killed"
    return f"Failed: {result.stderr}"


@tool
def system_services(action: str, service_name: str) -> str:
    """Manage system services (start, stop, restart, enable, disable, status)."""
    valid_actions = ["start", "stop", "restart", "enable", "disable", "status"]
    if action not in valid_actions:
        return f"Invalid action. Use: {', '.join(valid_actions)}"

    result = subprocess.run(
        f"sudo systemctl {action} {service_name} 2>&1",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


@tool
def disk_usage(path: str = "/") -> str:
    """Check disk usage for a path."""
    result = subprocess.run(f"df -h {path}", shell=True, capture_output=True, text=True)
    return result.stdout


@tool
def directory_size(path: str) -> str:
    """Show size of directories."""
    result = subprocess.run(
        f"du -sh {path}/* 2>/dev/null | sort -hr | head -15",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.stdout else "No data"


@tool
def network_info() -> str:
    """Show network connections and IP addresses."""
    result = subprocess.run(
        "ip addr show && echo '---' && nmcli device status",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


@tool
def system_info() -> str:
    """Show detailed system information."""
    result = subprocess.run(
        "uname -a && echo '---' && hostnamectl && echo '---' && uptime",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


@tool
def memory_info() -> str:
    """Show detailed memory information."""
    result = subprocess.run(
        "free -h && echo '---' && cat /proc/meminfo | head -10",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


@tool
def cpu_info() -> str:
    """Show detailed CPU information."""
    result = subprocess.run("lscpu", shell=True, capture_output=True, text=True)
    return result.stdout


@tool
def find_files(name: str, path: str = "/home") -> str:
    """Find files by name pattern."""
    result = subprocess.run(
        f"find {path} -name '*{name}*' 2>/dev/null | head -20",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.stdout else "No files found"


@tool
def list_services() -> str:
    """List all systemd services."""
    result = subprocess.run(
        "systemctl list-units --type=service --state=running | head -30",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


@tool
def firewall_status() -> str:
    """Check firewall status (ufw)."""
    result = subprocess.run(
        "sudo ufw status verbose 2>&1", shell=True, capture_output=True, text=True
    )
    return result.stdout + result.stderr


@tool
def search_web(query: str) -> str:
    """Search the web for information using ddgr."""
    result = subprocess.run(
        f"ddgr --json -n 5 {query} 2>/dev/null || echo 'ddgr not installed'",
        shell=True,
        capture_output=True,
        text=True,
    )
    if "ddgr not installed" in result.stdout:
        return "Web search not available. Install: sudo apt install ddgr"

    try:
        import json

        results = json.loads(result.stdout)
        output = []
        for r in results:
            output.append(f"- {r.get('title', 'N/A')}: {r.get('url', 'N/A')}")
        return "\n".join(output) if output else "No results found"
    except:
        return result.stdout


@tool
def run_command(command: str) -> str:
    """Run an arbitrary shell command. Use with caution - requires confirmation."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout + result.stderr


def get_tools():
    return [
        check_updates,
        upgrade_system,
        clean_system,
        detect_hardware,
        tune_performance,
        install_package,
        remove_package,
        search_package,
        add_repository,
        delete_path,
        create_desktop_icon,
        reorganize_documents,
        list_processes,
        kill_process,
        system_services,
        disk_usage,
        directory_size,
        network_info,
        system_info,
        memory_info,
        cpu_info,
        find_files,
        list_services,
        firewall_status,
        search_web,
        run_command,
    ]


def create_agent(model: str = DEFAULT_MODEL):
    llm = ChatOllama(
        model=model,
        temperature=0.1,
    )

    tools = get_tools()

    custom_instr = format_custom_instructions()

    distro_info = f"Detected Linux Distribution: {distro.distro.title()}\nPackage Manager: {distro.package_manager['name'].upper()}"

    system_prompt = f"""You are a Linux System Agent for Linux system management. You help users manage their system.
{distro_info}
{custom_instr}

IMPORTANT: Use the appropriate package manager commands for {distro.distro}. The detected package manager is: {distro.package_manager["name"]}

Available tools:
UPDATES & PACKAGES:
- check_updates: Check for package updates
- upgrade_system: Upgrade all packages  
- install_package: Install a package
- remove_package: Remove a package
- search_package: Search for a package
- add_repository: Add a PPA or repository

SYSTEM & HARDWARE:
- detect_hardware: Show CPU, RAM, disk info
- tune_performance: Optimize system based on hardware
- system_info: Show system information
- cpu_info: Show CPU details
- memory_info: Show memory details

FILES & STORAGE:
- disk_usage: Check disk space
- directory_size: Show directory sizes
- delete_path: Delete a file or folder
- find_files: Find files by name
- create_desktop_icon: Create launcher icon
- reorganize_documents: Organize ~/Documents

PROCESSES & SERVICES:
- list_processes: List running processes
- kill_process: Kill a process by PID
- system_services: Start/stop/restart/enable/disable/status services
- list_services: List all services
- firewall_status: Check firewall status

NETWORK:
- network_info: Show network connections and IP

SEARCH & UTILS:
- search_web: Search internet
- run_command: Run shell command

Always confirm dangerous operations (delete, remove package, kill process) before executing.
Provide clear feedback about what you're doing.
Be helpful and explain your actions."""

    agent = create_react_agent(llm, tools, prompt=system_prompt)
    return agent


def main():
    print("=" * 50)
    print(f"Linux System Agent - {distro.distro.title()}")
    print("=" * 50)
    print(f"Detected distro: {distro.distro.title()}")
    print(f"Package manager: {distro.package_manager['name'].upper()}")
    print(f"Available models: {', '.join(AVAILABLE_MODELS)}")
    print(f"Default model: {DEFAULT_MODEL}")
    print("\nTo change model, type: set model <model_name>")
    print("To manage instructions:")
    print("  add instruction <text>   - Add a custom instruction")
    print("  list instructions        - Show all custom instructions")
    print("  remove instruction <n>   - Remove instruction by number")
    print("  clear instructions       - Remove all custom instructions")
    print("To exit, type: exit\n")

    current_model = DEFAULT_MODEL
    agent = create_agent(current_model)

    while True:
        try:
            user_input = input("\033[92mYou:\033[0m ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

            if user_input.lower().startswith("add instruction "):
                new_instr = user_input[16:].strip()
                if new_instr:
                    instrs = load_instructions()
                    instrs.append(new_instr)
                    save_instructions(instrs)
                    agent = create_agent(current_model)
                    print(
                        f"\n\033[94mAgent:\033[0m Instruction added. Total: {len(instrs)}\n\n\n"
                    )
                else:
                    print(
                        f"\n\033[94mAgent:\033[0m Please provide instruction text.\n\n\n"
                    )
                continue

            if user_input.lower() == "list instructions":
                instrs = load_instructions()
                if instrs:
                    msg = "Custom instructions:\n"
                    for i, instr in enumerate(instrs, 1):
                        msg += f"{i}. {instr}\n"
                else:
                    msg = "No custom instructions set."
                print(f"\n\033[94mAgent:\033[0m {msg}\n\n\n")
                continue

            if user_input.lower().startswith("remove instruction "):
                try:
                    idx = int(user_input[18:].strip()) - 1
                    instrs = load_instructions()
                    if 0 <= idx < len(instrs):
                        removed = instrs.pop(idx)
                        save_instructions(instrs)
                        agent = create_agent(current_model)
                        print(f"\n\033[94mAgent:\033[0m Removed: {removed}\n\n\n")
                    else:
                        print(f"\n\033[94mAgent:\033[0m Invalid index.\n\n\n")
                except ValueError:
                    print(
                        f"\n\033[94mAgent:\033[0m Please provide a valid number.\n\n\n"
                    )
                continue

            if user_input.lower() == "clear instructions":
                save_instructions([])
                agent = create_agent(current_model)
                print(f"\n\033[94mAgent:\033[0m All instructions cleared.\n\n\n")
                continue

            if user_input.lower().startswith("set model "):
                new_model = user_input[10:].strip()
                if new_model in AVAILABLE_MODELS:
                    current_model = new_model
                    agent = create_agent(current_model)
                    print(
                        f"\n\033[94mAgent:\033[0m Model changed to {current_model}\n\n\n"
                    )
                else:
                    print(
                        f"\n\033[94mAgent:\033[0m Unknown model. Available: {', '.join(AVAILABLE_MODELS)}\n\n\n"
                    )
                continue

            result = agent.invoke({"messages": [("user", user_input)]})

            response = result["messages"][-1].content
            print(f"\n\033[94mAgent:\033[0m {response}\n\n\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
