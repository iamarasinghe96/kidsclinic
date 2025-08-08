# Clinic Management System - Desktop Installation

## Requirements
- Python 3.11 or higher
- pip (Python package installer)

## Installation Steps

1. **Install Python Dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```
   python main.py
   ```

3. **Access the Application**
   - Open your web browser
   - Go to: http://localhost:5000
   - Or for network access: http://0.0.0.0:5000

## Network Setup (For Multiple Computers)

To use this on multiple laptops in your clinic:

1. **Find your computer's IP address:**
   - Windows: Open Command Prompt, type `ipconfig`
   - Mac/Linux: Open Terminal, type `ifconfig` or `ip addr`
   - Look for your local IP (usually starts with 192.168.x.x)

2. **Start the application** on the main computer (where you installed it)

3. **Access from other computers:**
   - Open web browser on the second laptop
   - Go to: http://[YOUR-IP-ADDRESS]:5000
   - Example: http://192.168.1.100:5000

## Database
- Your patient data is stored in `instance/clinic.db`
- This file contains all patients, consultants, and visit records
- **IMPORTANT**: Back up this file regularly to prevent data loss

## Troubleshooting

**Port already in use error:**
- Change the port in main.py from 5000 to another port (like 5001)

**Can't access from other computers:**
- Check your firewall settings
- Make sure both computers are on the same WiFi network
- Try disabling Windows Firewall temporarily to test

**Database errors:**
- Delete the `instance/clinic.db` file to reset (you'll lose all data)
- Or restore from a backup

## Usage
- **Reception Interface**: http://[IP]:5000/reception
- **Consultant Interface**: http://[IP]:5000/consultant/[consultant-id]  
- **Reports**: http://[IP]:5000/report

Generated on: 2025-08-08 11:01:16
