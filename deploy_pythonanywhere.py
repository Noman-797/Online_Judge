#!/usr/bin/env python3
"""
Deployment script for PythonAnywhere
Run this script after uploading your project to PythonAnywhere
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description}")
        print(f"Error: {e.stderr}")
        return False
    return True

def main():
    print("🚀 Starting PythonAnywhere deployment...")
    
    # Create necessary directories
    directories = ['temp', 'staticfiles', 'media']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Install requirements
    if not run_command("pip3.13 install --user -r requirements_pythonanywhere.txt", 
                      "Installing Python packages"):
        return
    
    # Run migrations
    if not run_command("python3.13 manage.py migrate", 
                      "Running database migrations"):
        return
    
    # Collect static files
    if not run_command("python3.13 manage.py collectstatic --noinput", 
                      "Collecting static files"):
        return
    
    # Create superuser (optional)
    print("\n📝 To create a superuser, run:")
    print("python3.13 manage.py createsuperuser")
    
    print("\n✅ Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure your web app in PythonAnywhere dashboard")
    print("2. Set WSGI file to: /home/aasoj/Online_Judge/wsgi_pythonanywhere.py")
    print("3. Set static files URL to /static/ and directory to /home/aasoj/Online_Judge/staticfiles/")

if __name__ == "__main__":
    main()