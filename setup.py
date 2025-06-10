#!/usr/bin/env python
"""
Setup script for Walking Buddy Django Backend
This script automates the initial setup process.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_env_file():
    """Create .env file with default settings"""
    env_content = """# Django Settings
SECRET_KEY=django-insecure-change-this-in-production-1234567890
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Redis (for WebSocket and Celery)
REDIS_URL=redis://localhost:6379/0

# Media files
MEDIA_URL=/media/
MEDIA_ROOT=media/

# Static files
STATIC_URL=/static/
STATIC_ROOT=staticfiles/
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default settings")
    else:
        print("ℹ️  .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = ['media', 'staticfiles', 'media/photos', 'media/profiles']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")

def main():
    print("🚀 Walking Buddy Django Backend Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Create virtual environment
    if not Path('venv').exists():
        if not run_command('python -m venv venv', 'Creating virtual environment'):
            sys.exit(1)
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_cmd = 'venv\\Scripts\\pip'
        python_cmd = 'venv\\Scripts\\python'
    else:  # Unix/Linux/macOS
        pip_cmd = 'venv/bin/pip'
        python_cmd = 'venv/bin/python'
    
    if not run_command(f'{pip_cmd} install -r requirements.txt', 'Installing dependencies'):
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    # Run Django migrations
    if not run_command(f'{python_cmd} manage.py makemigrations', 'Creating database migrations'):
        sys.exit(1)
    
    if not run_command(f'{python_cmd} manage.py migrate', 'Applying database migrations'):
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start Redis server:")
    print("   - Windows: redis-server")
    print("   - macOS: brew services start redis")
    print("   - Linux: sudo systemctl start redis")
    print("\n2. Create a superuser:")
    print(f"   {python_cmd} manage.py createsuperuser")
    print("\n3. Run the development server:")
    print(f"   {python_cmd} manage.py runserver")
    print("\n4. Access the application:")
    print("   - Main app: http://localhost:8000")
    print("   - Admin panel: http://localhost:8000/admin")
    print("\n5. Optional - Run Celery for background tasks:")
    print(f"   {python_cmd} -m celery -A django_walking_buddy worker -l info")
    print(f"   {python_cmd} -m celery -A django_walking_buddy beat -l info")

if __name__ == '__main__':
    main() 