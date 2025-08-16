#!/bin/bash
cd "$(dirname "$0")"
echo "=========================================="
echo " THE KIDS CLINIC - RECEPTIONIST SYSTEM"
echo "=========================================="
echo ""
echo "Starting server on IP: 192.168.1.2:5000"
echo "Local access: http://localhost:5000/receptionist"
echo "Consultant access: http://192.168.1.2:5000/consultant"
echo "Reports: http://192.168.1.2:5000/report"
echo "Admin: http://192.168.1.2:5000/admin"
echo ""
echo "Opening receptionist interface in 3 seconds..."
sleep 3
open "http://localhost:5000/receptionist" 2>/dev/null || xdg-open "http://localhost:5000/receptionist" 2>/dev/null
echo ""
echo "Server is running... Do NOT close this window!"
echo ""
python3 main.py