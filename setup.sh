#!/bin/bash
#
# Linux System Agent Setup Script
# Supports: Ubuntu, Debian, Fedora, Arch, openSUSE, and derivatives
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="Linux System Agent"
APP_ID="linux-system-agent"
INSTALL_DIR="$HOME/.local/share/linux-system-agent"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons"
CONFIG_DIR="$HOME/.linux_agent"

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO="$ID"
        DISTRO_NAME="$NAME"
        DISTRO_VERSION="$VERSION_ID"
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        DISTRO="$DISTRIB_ID"
        DISTRO_NAME="$DISTRIB_DESCRIPTION"
        DISTRO_VERSION="$DISTRIB_RELEASE"
    else
        echo -e "${RED}Cannot detect Linux distribution${NC}"
        exit 1
    fi
    
    # Normalize distro names
    case "$DISTRO" in
        ubuntu|debian|linuxmint|pop)
            PKG_MANAGER="apt"
            PKG_INSTALL="sudo apt install -y"
            PKG_UPDATE="sudo apt update"
            PKG_SEARCH="apt search"
            PKG_REMOVE="sudo apt remove -y"
            SERVICE_MANAGER="systemctl"
            ;;
        fedora|rhel|centos|rocky|alma)
            PKG_MANAGER="dnf"
            PKG_INSTALL="sudo dnf install -y"
            PKG_UPDATE="sudo dnf check-update"
            PKG_SEARCH="dnf search"
            PKG_REMOVE="sudo dnf remove -y"
            SERVICE_MANAGER="systemctl"
            ;;
        arch|manjaro|endeavouros)
            PKG_MANAGER="pacman"
            PKG_INSTALL="sudo pacman -Sy --noconfirm"
            PKG_UPDATE="sudo pacman -Sy"
            PKG_SEARCH="pacman -Ss"
            PKG_REMOVE="sudo pacman -R --noconfirm"
            SERVICE_MANAGER="systemctl"
            ;;
        opensuse|sles)
            PKG_MANAGER="zypper"
            PKG_INSTALL="sudo zypper install -y"
            PKG_UPDATE="sudo zypper refresh"
            PKG_SEARCH="zypper search"
            PKG_REMOVE="sudo zypper remove -y"
            SERVICE_MANAGER="systemctl"
            ;;
        alpine)
            PKG_MANAGER="apk"
            PKG_INSTALL="sudo apk add"
            PKG_UPDATE="sudo apk update"
            PKG_SEARCH="apk search"
            PKG_REMOVE="sudo apk del"
            SERVICE_MANAGER="rc-service"
            ;;
        *)
            echo -e "${YELLOW}Warning: Unknown distribution: $DISTRO${NC}"
            echo -e "${YELLOW}Assuming apt-based system${NC}"
            PKG_MANAGER="apt"
            ;;
    esac
    
    echo -e "${GREEN}Detected:${NC} $DISTRO_NAME ($DISTRO)"
    echo -e "${GREEN}Package Manager:${NC} $PKG_MANAGER"
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${YELLOW}Warning: Running as root is not recommended${NC}"
    fi
}

# Check Python
check_python() {
    echo -e "${BLUE}Checking Python...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}Python found: $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}Python 3 not found. Installing...${NC}"
        case "$PKG_MANAGER" in
            apt) $PKG_INSTALL python3 python3-pip ;;
            dnf) $PKG_INSTALL python3 python3-pip ;;
            pacman) $PKG_INSTALL python python-pip ;;
            zypper) $PKG_INSTALL python3 python3-pip ;;
            apk) $PKG_INSTALL python3 py3-pip ;;
        esac
    fi
}

# Check and install Ollama
check_ollama() {
    echo -e "${BLUE}Checking Ollama...${NC}"
    if command -v ollama &> /dev/null; then
        OLLAMA_VERSION=$(ollama --version)
        echo -e "${GREEN}Ollama found: $OLLAMA_VERSION${NC}"
    else
        echo -e "${YELLOW}Ollama not found${NC}"
        read -p "Install Ollama? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_ollama
        fi
    fi
}

install_ollama() {
    echo -e "${BLUE}Installing Ollama...${NC}"
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Add to PATH temporarily
    export PATH="$PATH:/usr/local/bin:$HOME/.local/bin"
    
    # Start Ollama service
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable ollama 2>/dev/null || true
        sudo systemctl start ollama 2>/dev/null || true
    fi
    
    # Pull default model
    echo -e "${BLUE}Pulling default model (qwen2:7b)...${NC}"
    ollama pull qwen2:7b 2>/dev/null || echo -e "${YELLOW}Could not pull model automatically${NC}"
}

# Install required Python packages
install_python_deps() {
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    pip3 install langchain langchain-ollama langchain-community langgraph --break-system-packages 2>/dev/null || \
    pip3 install langchain langchain-ollama langchain-community langgraph
    echo -e "${GREEN}Python dependencies installed${NC}"
}

# Create application directory
create_dirs() {
    echo -e "${BLUE}Creating application directories...${NC}"
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$DESKTOP_DIR"
    mkdir -p "$ICON_DIR"
    mkdir -p "$CONFIG_DIR"
    echo -e "${GREEN}Directories created${NC}"
}

# Create desktop icon
create_desktop_icon() {
    echo -e "${BLUE}Creating desktop entry...${NC}"
    
    cat > "$DESKTOP_DIR/$APP_ID.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=AI-powered Linux system management agent
Exec=$INSTALL_DIR/linux_agent.py
Icon=terminal
Terminal=true
Categories=Utility;System;
Keywords=linux;agent;ai;system;management;admin;
StartupNotify=true
EOF

    chmod +x "$DESKTOP_DIR/$APP_ID.desktop"
    echo -e "${GREEN}Desktop entry created at $DESKTOP_DIR/$APP_ID.desktop${NC}"
}

# Create launcher script
create_launcher() {
    echo -e "${BLUE}Creating launcher script...${NC}"
    
    cat > "$INSTALL_DIR/linux_agent.sh" << EOF
#!/bin/bash
# Linux System Agent Launcher

# Add Ollama to PATH
export PATH="\$PATH:$HOME/.local/bin:/usr/local/bin"

# Set Python path
export PYTHONPATH="\$HOME/.local/lib/python3.12/site-packages:\$PYTHONPATH"

# Launch the agent
cd "$INSTALL_DIR"
exec python3 "$INSTALL_DIR/linux_agent.py" "\$@"
EOF

    chmod +x "$INSTALL_DIR/linux_agent.sh"
    
    # Also create python script wrapper
    cat > "$BIN_DIR/linux-agent" << EOF
#!/bin/bash
export PATH="\$PATH:$HOME/.local/bin:/usr/local/bin"
exec python3 "$INSTALL_DIR/linux_agent.py" "\$@"
EOF

    chmod +x "$BIN_DIR/linux-agent"
    echo -e "${GREEN}Launcher scripts created${NC}"
}

# Install the application
install_app() {
    echo -e "${BLUE}Installing application...${NC}"
    
    # Copy main application
    if [ -f "$(dirname "$0")/linux_agent.py" ]; then
        cp "$(dirname "$0")/linux_agent.py" "$INSTALL_DIR/"
        echo -e "${GREEN}Application copied${NC}"
    else
        echo -e "${RED}linux_agent.py not found in current directory${NC}"
        echo -e "${YELLOW}Please run this script from the project directory${NC}"
        exit 1
    fi
    
    # Make executable
    chmod +x "$INSTALL_DIR/linux_agent.py"
}

# Create default config
create_config() {
    echo -e "${BLUE}Creating default configuration...${NC}"
    
    if [ ! -f "$CONFIG_DIR/instructions.json" ]; then
        cat > "$CONFIG_DIR/instructions.json" << EOF
{
  "instructions": [],
  "distro": "$DISTRO",
  "package_manager": "$PKG_MANAGER"
}
EOF
        echo -e "${GREEN}Configuration created${NC}"
    fi
}

# Update desktop database
update_desktop_db() {
    echo -e "${BLUE}Updating desktop database...${NC}"
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
}

# Print summary
print_summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "To run the agent:"
    echo "  1. Start Ollama: ollama serve"
    echo "  2. Run: python3 $INSTALL_DIR/linux_agent.py"
    echo "     Or: $BIN_DIR/linux-agent"
    echo "     Or: from application menu (Utilities)"
    echo ""
    echo "Configuration: $CONFIG_DIR/instructions.json"
    echo ""
    echo "Detected Distribution: $DISTRO_NAME"
    echo "Package Manager: $PKG_MANAGER"
    echo ""
}

# Main installation flow
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Linux System Agent Setup${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    check_root
    detect_distro
    check_python
    check_ollama
    install_python_deps
    create_dirs
    install_app
    create_launcher
    create_desktop_icon
    create_config
    update_desktop_db
    print_summary
}

# Run main function
main "$@"
