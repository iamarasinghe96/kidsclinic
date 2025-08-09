
#!/bin/bash
echo "🏥 Clinic Management System - Dependency Installer"
echo "======================================================="
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    echo "Please install Python3 first:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"
echo

echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
fi

echo "✅ pip found: $(pip3 --version)"
echo

echo "Starting automatic installation..."
python3 install_dependencies.py

echo
echo "Installation complete!"
echo
read -p "Press Enter to continue..."
