"""
Install all project dependencies.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python packages from requirements.txt"""
    
    print("="*50)
    print("INSTALLING DEPENDENCIES")
    print("="*50)
    
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} not found!")
        return False
    
    print(f"\n📦 Installing packages from {requirements_file}...\n")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        
        print("\n" + "="*50)
        print("✅ ALL DEPENDENCIES INSTALLED!")
        print("="*50)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing dependencies: {e}")
        return False


def check_installation():
    """Verify key packages are installed."""
    
    print("\n📋 Verifying installation...\n")
    
    packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "streamlit",
        "google-generativeai",
        "google-cloud-speech",
        "sentence-transformers",
        "chromadb",
        "python-telegram-bot"
    ]
    
    all_installed = True
    
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            all_installed = False
    
    return all_installed


if __name__ == "__main__":
    success = install_requirements()
    
    if success:
        if check_installation():
            print("\n✅ All packages verified!")
        else:
            print("\n⚠️  Some packages may not have installed correctly")
    
    sys.exit(0 if success else 1)