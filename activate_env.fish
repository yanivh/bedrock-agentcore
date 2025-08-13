# Fish script to activate the virtual environment

# Check if .venv directory exists
if not test -d ".venv"
    echo "Error: .venv directory not found."
    echo "Please run setup_env.sh first to create the virtual environment."
    exit 1
end

# Check if activation script exists
if not test -f ".venv/bin/activate.fish"
    echo "Error: Virtual environment activation script not found."
    echo "Please run setup_env.sh first to properly set up the virtual environment."
    exit 1
end

echo "Activating virtual environment..."
source .venv/bin/activate.fish

# Verify activation
if test -n "$VIRTUAL_ENV"
    echo "✅ Virtual environment activated successfully!"
    echo "Python path: "(which python)
    echo "Python version: "(python --version)
    echo ""
    echo "To deactivate, run: deactivate"
else
    echo "❌ Failed to activate virtual environment."
    exit 1
end 