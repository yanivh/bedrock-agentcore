#!/bin/bash

# Script to activate the virtual environment

# Check if .venv directory exists
if [ ! -d ".venv" ]; then
    echo "Error: .venv directory not found."
    echo "Please run setup_env.sh first to create the virtual environment."
    exit 1
fi

# Check if activation script exists
if [ ! -f ".venv/bin/activate" ]; then
    echo "Error: Virtual environment activation script not found."
    echo "Please run setup_env.sh first to properly set up the virtual environment."
    exit 1
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# Verify activation
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment activated successfully!"
    echo "Python path: $(which python)"
    echo "Python version: $(python --version)"
    echo ""
    echo "To deactivate, run: deactivate"
else
    echo "❌ Failed to activate virtual environment."
    exit 1
fi 