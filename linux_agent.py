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
import time
from pathlib import Path
from typing import Optional, List

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

try:
    from config import load_config, save_config
except ImportError:

    def load_config():
        return {
            "search": {"rate_limit_per_minute": 5, "language": "en", "max_results": 5},
            "auto_fix": {"enabled": True, "ask_before_fix": True},
        }

    def save_config(cfg):
        pass


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


class SearchManager:
    """Manages web search with rate limiting and language support."""

    def __init__(self):
        self.config = load_config()
        self.request_times = []

    def can_search(self) -> bool:
        """Check if rate limit allows search (default: 5 per minute)."""
        import time

        now = time.time()
        limit = self.config.get("search", {}).get("rate_limit_per_minute", 5)

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        if len(self.request_times) < limit:
            self.request_times.append(now)
            return True
        return False

    def search(self, query: str, lang: Optional[str] = None) -> list:
        """Search the web using DuckDuckGo."""
        if lang is None:
            lang = self.config.get("search", {}).get("language", "en")

        if not self.can_search():
            return [
                {"error": "Rate limit exceeded. Please wait before searching again."}
            ]

        try:
            from duckduckgo_search import DDGS

            max_results = self.config.get("search", {}).get("max_results", 5)

            ddgs = DDGS()
            results = list(
                ddgs.text(
                    query,
                    max_results=max_results,
                    region=lang if lang != "en" else "wt-wt",
                )
            )

            return results if results else [{"error": "No results found."}]
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]

    def fetch_url(self, url: str) -> str:
        """Fetch and parse content from a URL."""
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text(separator="\n", strip=True)

            # Limit to first 3000 chars
            return text[:3000] if len(text) > 3000 else text
        except Exception as e:
            return f"Failed to fetch URL: {str(e)}"


class ErrorDetector:
    """Detects and classifies system errors."""

    ERROR_PATTERNS = {
        "package": [
            r"E: Package .* not found",
            r"dpkg: error",
            r"Unable to locate package",
            r"dependency problems",
            r"broken packages",
            r"could not be satisfied",
        ],
        "service": [
            r"Failed to start .* service",
            r"active: failed",
            r"Unit .* failed",
            r"Job for .* failed",
            r"Failed to restart",
        ],
        "network": [
            r"network unreachable",
            r"dns.*error",
            r"connection refused",
            r"Could not resolve",
            r"Temporary failure in name resolution",
        ],
        "permission": [
            r"permission denied",
            r"sudo:.*not found",
            r"Operation not permitted",
        ],
        "disk": [
            r"No space left on device",
            r"Disk quota exceeded",
            r"read-only file system",
        ],
    }

    def detect(self, error_output: str) -> tuple[str, str]:
        """Detect error type and return (category, description)."""
        import re

        for category, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, error_output, re.IGNORECASE):
                    return category, pattern

        return "unknown", "Unknown error"


class FixManager:
    """Manages fixes for detected errors."""

    FIX_STRATEGIES = {
        "package": [
            "Run package manager update (e.g., 'sudo apt update')",
            "Check package name spelling",
            "Add required repository (e.g., 'sudo add-apt-repository ppa:user/ppa')",
            "Try installing dependencies first",
        ],
        "service": [
            "Check service status: sudo systemctl status <service>",
            "View detailed logs: sudo journalctl -xe -u <service>",
            "Reload systemd daemon: sudo systemctl daemon-reload",
            "Check if port is already in use",
        ],
        "network": [
            "Check network connection: ping -c 3 8.8.8.8",
            "Check DNS: cat /etc/resolv.conf",
            "Restart network manager: sudo systemctl restart NetworkManager",
            "Check firewall rules",
        ],
        "permission": [
            "Use sudo for privileged commands",
            "Check file permissions: ls -la <path>",
            "Add user to appropriate group: sudo usermod -aG <group> <user>",
        ],
        "disk": [
            "Clean up disk space: 'clean system' command",
            "Remove old logs: sudo journalctl --vacuum-time=7d",
            "Check disk usage: 'disk usage' command",
        ],
    }

    def get_fix(self, error_category: str) -> str:
        """Return suggested fix for error category."""
        strategies = self.FIX_STRATEGIES.get(
            error_category, ["Try the command again", "Check system logs"]
        )
        return "\n".join([f"- {s}" for s in strategies])


# Global instances
search_manager = SearchManager()
error_detector = ErrorDetector()
fix_manager = FixManager()


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

    output = result.stdout + result.stderr

    if result.returncode != 0:
        category, pattern = error_detector.detect(output)
        fix_suggestions = fix_manager.get_fix(category)

        output += f"\n\n" + "=" * 50 + "\n"
        output += f"Error detected! Category: {category.upper()}\n"
        output += f"\nSuggested fixes:\n{fix_suggestions}\n"

        results = search_manager.search(f"{distro.distro} system upgrade error fix")
        if results and "error" not in results[0]:
            output += "\nOnline solutions:\n"
            for r in results[:3]:
                output += f"• {r.get('title', 'N/A')}: {r.get('href', 'N/A')}\n"

    return output


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

    output = result.stdout + result.stderr

    # Check for errors and provide diagnosis
    if result.returncode != 0:
        category, pattern = error_detector.detect(output)
        fix_suggestions = fix_manager.get_fix(category)

        output += f"\n\n" + "=" * 50 + "\n"
        output += f"Error detected! Category: {category.upper()}\n"
        output += f"\nSuggested fixes:\n{fix_suggestions}\n"

        # Add online search results
        results = search_manager.search(
            f"Ubuntu {package_name} install error {pattern} fix"
        )
        if results and "error" not in results[0]:
            output += "\nOnline solutions:\n"
            for r in results[:3]:
                output += f"• {r.get('title', 'N/A')}: {r.get('href', 'N/A')}\n"

    return output


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

    output = result.stdout + result.stderr

    if result.returncode != 0:
        category, pattern = error_detector.detect(output)
        fix_suggestions = fix_manager.get_fix(category)

        output += f"\n\n" + "=" * 50 + "\n"
        output += f"Error detected! Category: {category.upper()}\n"
        output += f"\nSuggested fixes:\n{fix_suggestions}\n"

        results = search_manager.search(f"systemd {service_name} {action} failed fix")
        if results and "error" not in results[0]:
            output += "\nOnline solutions:\n"
            for r in results[:3]:
                output += f"• {r.get('title', 'N/A')}: {r.get('href', 'N/A')}\n"

    return output


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
def search_web(query: str, language: str = "en") -> str:
    """Search the web for information using DuckDuckGo.

    Args:
        query: The search query
        language: 'en' for English, 'ar' for Arabic (default: en)
    """
    results = search_manager.search(query, language)

    if isinstance(results, list) and "error" in results[0] if results else False:
        return results[0]["error"]

    output = []
    for r in results:
        title = r.get("title", "N/A")
        url = r.get("href", r.get("url", "N/A"))
        body = r.get("body", "")[:100]
        output.append(f"• {title}\n  {body}...\n  URL: {url}\n")

    return "\n".join(output) if output else "No results found."


@tool
def fetch_url(url: str) -> str:
    """Fetch content from a URL and extract key information.

    Args:
        url: The URL to fetch
    """
    return search_manager.fetch_url(url)


@tool
def diagnose_error(error_message: str) -> str:
    """Diagnose a system error and find solutions online.

    Args:
        error_message: The error message to diagnose
    """
    category, pattern = error_detector.detect(error_message)

    if category == "unknown":
        # Search online for the error
        results = search_manager.search(f"Linux {error_message[:100]} fix solution")
        output = [f"Error detected but couldn't classify. Searching online...\n"]
        for r in results[:3]:
            output.append(f"• {r.get('title', 'N/A')}: {r.get('href', 'N/A')}")
        return "\n".join(output)

    fix_suggestions = fix_manager.get_fix(category)

    # Search for specific solutions
    results = search_manager.search(f"{category} {error_message[:50]} fix")

    output = [
        f"Error Category: {category.upper()}",
        f"Matched Pattern: {pattern}",
        "",
        "General Fix Suggestions:",
        fix_suggestions,
        "",
        "Online Solutions:",
    ]

    for r in results[:3]:
        output.append(f"• {r.get('title', 'N/A')}: {r.get('href', 'N/A')}")

    return "\n".join(output)


@tool
def search_documentation(topic: str) -> str:
    """Search official Linux documentation (Arch Wiki, Ubuntu Docs).

    Args:
        topic: The topic to search for
    """
    results = search_manager.search(f"site:wiki.archlinux.org {topic}")

    if not results:
        return f"No documentation found for '{topic}'"

    output = [f"Documentation results for '{topic}':\n"]
    for r in results[:5]:
        output.append(f"• {r.get('title', 'N/A')}\n  {r.get('href', 'N/A')}\n")

    return "\n".join(output)


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
        fetch_url,
        diagnose_error,
        search_documentation,
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
- search_web: Search internet (supports English and Arabic)
- fetch_url: Fetch and parse content from a URL
- search_documentation: Search official Linux docs (Arch Wiki, Ubuntu Docs)
- diagnose_error: Diagnose error and find solutions online
- run_command: Run shell command

ERROR HANDLING:
When commands fail, the agent will automatically detect the error type (package, service, network, permission, disk) and provide suggested fixes with online solutions.

CONFIGURATION:
- Search rate limit: 5/minute (configurable 1-20)
- Search language: English (en) or Arabic (ar)
- Auto-fix: enabled by default

Always confirm dangerous operations (delete, remove package, kill process) before executing.
Provide clear feedback about what you're doing.
Be helpful and explain your actions."""

    agent = create_react_agent(llm, tools, prompt=system_prompt)
    return agent


def main():
    config = load_config()

    print("=" * 50)
    print(f"Linux System Agent - {distro.distro.title()}")
    print("=" * 50)
    print(f"Detected distro: {distro.distro.title()}")
    print(f"Package manager: {distro.package_manager['name'].upper()}")
    print(f"Available models: {', '.join(AVAILABLE_MODELS)}")
    print(f"Default model: {DEFAULT_MODEL}")
    print(
        f"\nSearch language: {config.get('search', {}).get('language', 'en').upper()}"
    )
    print(
        f"Search rate limit: {config.get('search', {}).get('rate_limit_per_minute', 5)}/min"
    )
    print(
        f"Auto-fix: {'enabled' if config.get('auto_fix', {}).get('enabled', True) else 'disabled'}"
    )
    print("\nTo change model, type: set model <model_name>")
    print("To manage instructions:")
    print("  add instruction <text>   - Add a custom instruction")
    print("  list instructions        - Show all custom instructions")
    print("  remove instruction <n>   - Remove instruction by number")
    print("  clear instructions       - Remove all custom instructions")
    print("To manage config:")
    print("  set search limit <n>     - Set searches per minute (1-20)")
    print("  set language <en|ar>     - Set search language")
    print("  show config              - Display current settings")
    print("To exit, type: exit\n")

    current_model = DEFAULT_MODEL
    agent = create_agent(current_model)

    while True:
        try:
            try:
                user_input = input("\033[92mYou:\033[0m ").strip()
            except EOFError:
                break
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

            if user_input.lower().startswith("set search limit "):
                try:
                    limit = int(user_input[16:].strip())
                    if 1 <= limit <= 20:
                        config["search"]["rate_limit_per_minute"] = limit
                        save_config(config)
                        print(
                            f"\n\033[94mAgent:\033[0m Search limit set to {limit}/min\n\n\n"
                        )
                    else:
                        print(
                            f"\n\033[94mAgent:\033[0m Limit must be between 1 and 20\n\n\n"
                        )
                except ValueError:
                    print(
                        f"\n\033[94mAgent:\033[0m Please provide a valid number\n\n\n"
                    )
                continue

            if user_input.lower().startswith("set language "):
                lang = user_input[12:].strip().lower()
                if lang in ["en", "ar"]:
                    config["search"]["language"] = lang
                    save_config(config)
                    print(
                        f"\n\033[94mAgent:\033[0m Language set to {lang.upper()}\n\n\n"
                    )
                else:
                    print(
                        f"\n\033[94mAgent:\033[0m Invalid language. Use 'en' or 'ar'\n\n\n"
                    )
                continue

            if user_input.lower() == "show config":
                msg = f"""Current Configuration:
Search Language: {config.get("search", {}).get("language", "en").upper()}
Search Rate Limit: {config.get("search", {}).get("rate_limit_per_minute", 5)}/min
Max Results: {config.get("search", {}).get("max_results", 5)}
Auto-fix Enabled: {config.get("auto_fix", {}).get("enabled", True)}
Ask Before Fix: {config.get("auto_fix", {}).get("ask_before_fix", True)}
Model: {current_model}"""
                print(f"\n\033[94mAgent:\033[0m {msg}\n\n\n")
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
