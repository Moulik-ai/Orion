#!/bin/bash

# Orion Voice Assistant - Cross-platform Setup Script
# This script creates a Python virtual environment and installs dependencies

set -e  # Exit on error

echo "================================================"
echo "  Orion Voice Assistant - Setup Script"
echo "================================================"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=macOS;;
    CYGWIN*|MINGW*|MSYS*) PLATFORM=Windows;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "Detected platform: ${PLATFORM}"
echo ""

# Windows-specific instructions
if [[ "${PLATFORM}" == "Windows" ]]; then
    echo "==============================================="
    echo "  WINDOWS USERS: Manual Setup Required"
    echo "==============================================="
    echo ""
    echo "This script is designed for Linux/macOS."
    echo "For Windows, please follow these steps:"
    echo ""
    echo "1. Install Python 3.7+ from python.org"
    echo "2. Open PowerShell or Command Prompt"
    echo "3. Create virtual environment:"
    echo "   python -m venv venv"
    echo ""
    echo "4. Activate virtual environment:"
    echo "   venv\\Scripts\\activate"
    echo ""
    echo "5. Install dependencies:"
    echo "   pip install -r requirements.txt"
    echo ""
    echo "6. Run Orion:"
    echo "   python orion.py"
    echo ""
    echo "Note: PyAudio on Windows may require:"
    echo "  - Microsoft Visual C++ Build Tools, or"
    echo "  - Pre-built wheel from:"
    echo "    https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio"
    echo ""
    echo "Note: pywin32 should install normally via pip on Windows."
    echo "================================================"
    exit 0
fi

# Linux/macOS setup continues below

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.7 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Found: ${PYTHON_VERSION}"
echo ""

# Platform-specific dependencies warning
if [[ "${PLATFORM}" == "Linux" ]]; then
    echo "================================================"
    echo "  Linux Users: PortAudio Required for PyAudio"
    echo "================================================"
    echo ""
    echo "If PyAudio installation fails, install PortAudio first:"
    echo "  Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-pyaudio"
    echo "  Fedora/RHEL:   sudo dnf install portaudio-devel"
    echo "  Arch:          sudo pacman -S portaudio"
    echo ""
    read -p "Press Enter to continue..."
    echo ""
elif [[ "${PLATFORM}" == "macOS" ]]; then
    echo "================================================"
    echo "  macOS Users: PortAudio Required for PyAudio"
    echo "================================================"
    echo ""
    echo "If PyAudio installation fails, install PortAudio via Homebrew:"
    echo "  brew install portaudio"
    echo ""
    read -p "Press Enter to continue..."
    echo ""
fi

# Create virtual environment
VENV_DIR="./venv"
echo "Creating Python virtual environment in ${VENV_DIR}..."

if [ -d "${VENV_DIR}" ]; then
    echo "Warning: Virtual environment already exists."
    read -p "Remove and recreate? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "${VENV_DIR}"
        python3 -m venv "${VENV_DIR}"
    else
        echo "Skipping venv creation."
    fi
else
    python3 -m venv "${VENV_DIR}"
fi

echo "Virtual environment created."
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source "${VENV_DIR}/bin/activate"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo ""

# Install requirements
echo "Installing dependencies from requirements.txt..."
echo ""

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    INSTALL_STATUS=$?
    echo ""
    
    if [ $INSTALL_STATUS -eq 0 ]; then
        echo "================================================"
        echo "  Setup Complete!"
        echo "================================================"
    else
        echo "================================================"
        echo "  Setup Completed with Warnings"
        echo "================================================"
        echo ""
        echo "Some packages may have failed to install."
        echo "Please review the error messages above."
    fi
else
    echo "ERROR: requirements.txt not found in current directory."
    exit 1
fi

echo ""
echo "Next steps:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run Orion:"
echo "     python orion.py"
echo ""
echo "  3. When finished, deactivate the virtual environment:"
echo "     deactivate"
echo ""
echo "================================================"
echo ""

# Deactivate for now (user will reactivate when ready)
deactivate
