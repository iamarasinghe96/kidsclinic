#!/bin/bash
echo "=========================================="
echo "  THE KIDS CLINIC - CONSULTANT VIEW"
echo "=========================================="
echo ""
echo "Connecting to receptionist computer..."
echo "Server IP: 192.168.1.2:5000"
echo ""
echo "Testing connection..."
if ping -c 2 192.168.1.2 > /dev/null 2>&1; then
    echo "Connection successful!"
    echo "Opening consultant view in 3 seconds..."
    sleep 3
    open "http://192.168.1.2:5000/consultant" 2>/dev/null || xdg-open "http://192.168.1.2:5000/consultant" 2>/dev/null
    echo ""
    echo "Consultant interface is now open."
    echo "This window can be closed."
else
    echo "ERROR: Cannot connect to receptionist computer!"
    echo "Please ensure:"
    echo "1. Receptionist computer is turned on"
    echo "2. Receptionist has started the server"
    echo "3. Both computers are on same network"
    echo "4. Server IP is 192.168.1.2"
    read -p "Press Enter to close..."
fi