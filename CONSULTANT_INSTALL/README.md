
# CONSULTANT LAPTOP INSTALLATION

## Quick Installation Steps

1. **Extract this folder** to `C:\ClinicApp\CONSULTANT_INSTALL\`

2. **Get the receptionist laptop's IP address** (example: 192.168.1.100)

3. **Right-click on `install.bat`** and select **"Run as administrator"**

4. **Enter the receptionist IP** when prompted

5. **Start the system** by double-clicking the desktop shortcut **"Start Clinic - Consultant"**

## What the installer does:
- ✓ Installs required packages
- ✓ Creates desktop shortcut configured for your receptionist's IP
- ✓ Sets up automatic connection to receptionist system

## Daily Usage:
1. Double-click **"Start Clinic - Consultant"** on desktop
2. Browser opens automatically to the consultant view
3. Select your name from the dropdown menu
4. View patients assigned by receptionist

## Getting Receptionist IP:
Ask the receptionist to:
1. Press `Windows + R`, type `cmd`, press Enter
2. Type `ipconfig` and press Enter
3. Find "IPv4 Address" (example: 192.168.1.100)

## Setup Printer Sharing:
1. Go to Settings > Devices > Printers & scanners
2. Select your printer > Manage > Printer properties
3. Go to "Sharing" tab > Check "Share this printer"
4. Note the share name for receptionist setup

## Troubleshooting:
- If connection fails: Check receptionist system is running
- If shortcut doesn't work: Run `start_consultant.bat` directly
- Network issues: Ensure both laptops on same WiFi
