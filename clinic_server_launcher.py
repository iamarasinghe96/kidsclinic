
#!/usr/bin/env python3
"""
Clinic Management System Server Launcher
Run this on the receptionist's laptop to start the database server
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
import socket
import webbrowser
import threading
import time

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def check_port_available(port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return True
    except:
        return False

def start_server():
    """Start the Flask server"""
    if not check_port_available(5000):
        messagebox.showerror(
            "Port Error", 
            "Port 5000 is already in use.\nPlease close any other applications using this port and try again."
        )
        return False
    
    try:
        # Start the server in a separate process
        if sys.platform.startswith('win'):
            subprocess.Popen([sys.executable, "main.py"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen([sys.executable, "main.py"])
        
        return True
    except Exception as e:
        messagebox.showerror("Server Error", f"Failed to start server:\n{str(e)}")
        return False

def create_server_gui():
    """Create the server control GUI"""
    root = tk.Tk()
    root.title("Clinic Management Server")
    root.geometry("500x400")
    root.resizable(False, False)
    
    # Get local IP
    local_ip = get_local_ip()
    
    # Header
    header = tk.Label(root, text="🏥 Clinic Management System", 
                     font=("Arial", 16, "bold"), fg="blue")
    header.pack(pady=10)
    
    subtitle = tk.Label(root, text="Server Control Panel (Receptionist's Laptop)", 
                       font=("Arial", 12))
    subtitle.pack(pady=5)
    
    # Server info frame
    info_frame = tk.Frame(root, relief=tk.SUNKEN, bd=2)
    info_frame.pack(pady=10, padx=20, fill=tk.X)
    
    tk.Label(info_frame, text="Server Information:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=5)
    tk.Label(info_frame, text=f"IP Address: {local_ip}", font=("Arial", 10)).pack(anchor=tk.W, padx=20)
    tk.Label(info_frame, text="Port: 5000", font=("Arial", 10)).pack(anchor=tk.W, padx=20)
    tk.Label(info_frame, text=f"Reception URL: http://{local_ip}:5000/reception", font=("Arial", 9)).pack(anchor=tk.W, padx=20)
    tk.Label(info_frame, text=f"Reports URL: http://{local_ip}:5000/report", font=("Arial", 9)).pack(anchor=tk.W, padx=20, pady=(0,10))
    
    # Instructions
    instructions = tk.Text(root, height=8, width=60, wrap=tk.WORD)
    instructions.pack(pady=10, padx=20)
    instructions.insert(tk.END, f"""Instructions for setting up other laptops:

1. Note down this laptop's IP address: {local_ip}

2. On the consultant's laptop:
   - Copy the clinic management files
   - Run 'python create_clinic_shortcuts.py'
   - Enter this IP address: {local_ip}
   - Use the created desktop shortcuts

3. Network Requirements:
   - Both laptops must be on the same WiFi network
   - Firewall may need to allow port 5000
   - No internet connection required

4. Database Location:
   - All data is stored on THIS laptop in 'instance/clinic.db'
   - Back up this file regularly""")
    instructions.config(state=tk.DISABLED)
    
    # Buttons frame
    buttons_frame = tk.Frame(root)
    buttons_frame.pack(pady=20)
    
    def start_and_open():
        if start_server():
            messagebox.showinfo("Server Started", 
                              f"Server started successfully!\n\nReception: http://{local_ip}:5000/reception\nReports: http://{local_ip}:5000/report")
            # Wait a moment then open browser
            threading.Thread(target=lambda: (time.sleep(2), webbrowser.open(f"http://{local_ip}:5000/reception"))).start()
    
    start_btn = tk.Button(buttons_frame, text="🚀 Start Server & Open Reception", 
                         command=start_and_open, bg="green", fg="white", 
                         font=("Arial", 10, "bold"), padx=20, pady=10)
    start_btn.pack(side=tk.LEFT, padx=10)
    
    def open_reception():
        webbrowser.open(f"http://{local_ip}:5000/reception")
    
    reception_btn = tk.Button(buttons_frame, text="📋 Open Reception", 
                            command=open_reception, bg="blue", fg="white", 
                            font=("Arial", 10), padx=20, pady=10)
    reception_btn.pack(side=tk.LEFT, padx=5)
    
    def open_reports():
        webbrowser.open(f"http://{local_ip}:5000/report")
    
    reports_btn = tk.Button(buttons_frame, text="📊 Open Reports", 
                          command=open_reports, bg="orange", fg="white", 
                          font=("Arial", 10), padx=20, pady=10)
    reports_btn.pack(side=tk.LEFT, padx=5)
    
    # Footer
    footer = tk.Label(root, text="Keep this window open while the system is in use", 
                     font=("Arial", 9), fg="gray")
    footer.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    # Try to find main.py in current directory or parent directories
    current_dir = os.getcwd()
    main_py_path = None
    
    # Check current directory
    if os.path.exists("main.py"):
        main_py_path = "main.py"
    # Check if we're in a subdirectory - look one level up
    elif os.path.exists("../main.py"):
        os.chdir("..")
        main_py_path = "main.py"
    # Check in clinic_desktop_export directory
    elif os.path.exists("clinic_desktop_export/main.py"):
        os.chdir("clinic_desktop_export")
        main_py_path = "main.py"
    
    if not main_py_path:
        messagebox.showerror(
            "File Error", 
            f"main.py not found!\n\nCurrent directory: {current_dir}\n\nPlease ensure you're running this from the clinic management directory or that main.py exists."
        )
        sys.exit(1)
    
    create_server_gui()
