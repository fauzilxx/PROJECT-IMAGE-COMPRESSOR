#!/usr/bin/env python3
"""
Script untuk menjalankan aplikasi PCA Image Compression
"""

import os
import sys
import shutil

def create_directories():
    """Create required directories"""
    dirs = ['templates', 'static', 'temp']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ Created directory: {dir_name}/")

def create_template_file():
    """Membuat file template HTML"""
    template_dir = 'templates'
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # Template HTML akan dibuat secara manual
    # Karena terlalu panjang untuk dimasukkan dalam script ini
    print(f"Pastikan file 'index.html' ada di folder '{template_dir}/'")

def check_dependencies():
    """Cek apakah semua dependencies sudah terinstall"""
    required_packages = [
        'flask', 'numpy', 'PIL', 'sklearn', 'pandas'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'sklearn':
                import sklearn
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_required_files():
    """Check if all required files exist"""
    required_files = {
        'templates/index.html': 'HTML template',
        'static/style.css': 'CSS styles',
        'static/script.js': 'JavaScript code',
        'app.py': 'Flask application',
    }
    
    missing_files = []
    for file_path, description in required_files.items():
        if not os.path.exists(file_path):
            missing_files.append(f"   - {file_path} ({description})")
    
    if missing_files:
        print("❌ Missing files:")
        print("\n".join(missing_files))
        return False
    
    print("✅ All required files are present!")
    return True

def main():
    print("🚀 PCA Image Compression Setup")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Check dependencies and files
    if not check_dependencies() or not check_required_files():
        sys.exit(1)
    
    print("\n📁 Folder structure:")
    print("   ├── app.py (Flask application)")
    print("   ├── templates/")
    print("   │   └── index.html (HTML template)")
    print("   ├── static/")
    print("   │   ├── style.css (CSS styles)")
    print("   │   └── script.js (JavaScript code)")
    print("   ├── temp/ (will be created for downloads)")
    print("   └── requirements.txt")
    
    print("\n🌐 Starting Flask application...")
    print("   URL: http://127.0.0.1:5000")
    print("   Press Ctrl+C to stop")
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, host='127.0.0.1', port=5000)
    except ImportError:
        print("❌ Error: app.py not found!")
        print("   Make sure app.py is in the same directory")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == '__main__':
    main()