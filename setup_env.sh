#!/bin/bash
set -e

# Check for Python 3.x (latest)
PYTHON_BIN=$(command -v python3 || true)
if [ -z "$PYTHON_BIN" ]; then
  echo "Python 3 is required but not found. Please install Python 3.10 or newer."
  exit 1
fi

PYTHON_VERSION=$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION < 3.10" | bc) -eq 1 ]]; then
  echo "Python 3.10 or newer is required. Found $PYTHON_VERSION."
  exit 1
fi

echo "Using Python $PYTHON_VERSION at $PYTHON_BIN"

# Install uv if not present
if ! command -v uv &> /dev/null; then
  echo "Installing uv..."
  $PYTHON_BIN -m pip install --upgrade pip
  $PYTHON_BIN -m pip install uv
else
  echo "uv is already installed."
fi

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment with uv..."
  uv venv --python $PYTHON_BIN
else
  echo ".venv already exists."
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# Initialize uv project if not already
if [ ! -f "uv.toml" ]; then
  echo "Initializing uv project..."
  uv init
fi

# Install dependencies
if [ -f "requirements.txt" ]; then
  echo "Installing dependencies from requirements.txt..."
  uv pip install -r requirements.txt
else
  echo "requirements.txt not found. Skipping dependency installation."
fi

echo "Environment setup complete." 