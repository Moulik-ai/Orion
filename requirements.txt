#!/usr/bin/env bash
set -euo pipefail

echo "Orion setup script"
echo

# Detect platform
OS_TYPE="unknown"
if [ -n "${OS:-}" ] && [ "${OS}" = "Windows_NT" ]; then
  OS_TYPE="windows"
else
  UNAME_OUT="$(uname -s || true)"
  case "${UNAME_OUT}" in
    Linux*)     OS_TYPE="linux";;
    Darwin*)    OS_TYPE="macos";;
    CYGWIN*|MINGW*|MSYS*) OS_TYPE="windows";;
    *)          OS_TYPE="unix";;
  esac
fi

echo "Detected platform: ${OS_TYPE}"
echo

if [ "${OS_TYPE}" = "windows" ]; then
  cat <<'WARN'
Windows users:
- Installing PyAudio and pywin32 can require prebuilt wheels or additional steps.
- Recommended: use pipwin to install PyAudio on Windows:
    pip install pipwin
    pipwin install pyaudio
  or download matching wheels from:
    https://www.lfd.uci.edu/~gohlke/pythonlibs/
- For pywin32, pip usually works:
    pip install pywin32
WARN
fi

# Create venv
VENV_DIR="./venv"
if [ -d "${VENV_DIR}" ]; then
  echo "Virtual environment directory ${VENV_DIR} already exists."
else
  echo "Creating virtual environment at ${VENV_DIR}..."
  # Try python3 then python
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv "${VENV_DIR}"
  else
    python -m venv "${VENV_DIR}"
  fi
  echo "Virtual environment created."
fi

# Install requirements into the venv (without activating it)
if [ "${OS_TYPE}" = "windows" ]; then
  PIP_BIN="${VENV_DIR}\\Scripts\\pip.exe"
else
  PIP_BIN="${VENV_DIR}/bin/pip"
fi

if [ ! -x "${PIP_BIN}" ] && [ ! -f "${PIP_BIN}" ]; then
  echo "pip executable not found in virtualenv at ${PIP_BIN}."
  echo "Please activate the virtualenv and install requirements manually."
  echo "Activation (example):"
  echo "  source ${VENV_DIR}/bin/activate   # unix / macOS"
  echo "  .\\${VENV_DIR}\\Scripts\\Activate.ps1  # PowerShell on Windows"
  exit 1
fi

echo "Installing dependencies from requirements.txt into the virtualenv..."
"${PIP_BIN}" install --upgrade pip
"${PIP_BIN}" install -r requirements.txt

echo
echo "Setup complete."
echo
if [ "${OS_TYPE}" = "windows" ]; then
  echo "To activate the virtualenv (PowerShell):"
  echo "  .\\${VENV_DIR}\\Scripts\\Activate.ps1"
else
  echo "To activate the virtualenv (bash/zsh):"
  echo "  source ${VENV_DIR}/bin/activate"
fi
echo "Then run:"
echo "  python orion.py"
