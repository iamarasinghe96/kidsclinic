
#!/usr/bin/env python3
"""
Automatic dependency installer for Clinic Management System
Run this first to install all required packages
"""
import sys
import subprocess
import platform

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_packages():
    """Check and install all required packages"""
    print("🏥 Clinic Management System - Dependency Installer")
    print("=" * 60)
    
    # Basic packages for all systems
    packages = [
        'flask>=3.1.1',
        'flask-sqlalchemy>=3.1.1', 
        'sqlalchemy>=2.0.42',
        'werkzeug>=3.1.3',
        'email-validator>=2.2.0',
        'pytz>=2025.2',
        'requests>=2.31.0'
    ]
    
    # Windows-specific packages for shortcuts
    if platform.system() == "Windows":
        packages.extend([
            'pywin32',
            'winshell'
        ])
        print("🪟 Detected Windows - including shortcut creation packages")
    
    print(f"\n📦 Installing {len(packages)} packages...")
    
    failed_packages = []
    for i, package in enumerate(packages, 1):
        print(f"[{i}/{len(packages)}] Installing {package}...", end=" ")
        if install_package(package):
            print("✅")
        else:
            print("❌")
            failed_packages.append(package)
    
    print("\n" + "=" * 60)
    
    if failed_packages:
        print("❌ Some packages failed to install:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n💡 Try running these manually:")
        for package in failed_packages:
            print(f"   pip install {package}")
        return False
    else:
        print("✅ All packages installed successfully!")
        print("\n🚀 Next steps:")
        print("1. For RECEPTIONIST laptop: Run 'python clinic_server_launcher.py'")
        print("2. For CONSULTANT laptop: Run 'python create_clinic_shortcuts.py'")
        return True

if __name__ == "__main__":
    success = check_and_install_packages()
    input(f"\nPress Enter to exit...")
    sys.exit(0 if success else 1)
