#!/usr/bin/env python3
"""
Health check script for Online Judge system
"""
import os
import sys
import subprocess
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from problems.models import Problem, Category
from submissions.models import Submission

def check_database():
    """Check database connectivity"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database connection: OK")
        return True
    except Exception as e:
        print(f"✗ Database connection: FAILED - {e}")
        return False

def check_models():
    """Check if models are working"""
    try:
        user_count = User.objects.count()
        problem_count = Problem.objects.count()
        category_count = Category.objects.count()
        submission_count = Submission.objects.count()
        
        print(f"✓ Models: OK")
        print(f"  - Users: {user_count}")
        print(f"  - Problems: {problem_count}")
        print(f"  - Categories: {category_count}")
        print(f"  - Submissions: {submission_count}")
        return True
    except Exception as e:
        print(f"✗ Models: FAILED - {e}")
        return False

def check_compilers():
    """Check if compilers are available"""
    compilers = {
        'gcc': 'gcc --version',
        'g++': 'g++ --version',
        'python3': 'python3 --version'
    }
    
    all_ok = True
    for name, cmd in compilers.items():
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"✓ {name}: {version}")
            else:
                print(f"✗ {name}: Not available")
                all_ok = False
        except Exception as e:
            print(f"✗ {name}: FAILED - {e}")
            all_ok = False
    
    return all_ok

def check_directories():
    """Check if required directories exist"""
    dirs = ['temp', 'static', 'templates', 'media']
    all_ok = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✓ Directory {dir_name}: OK")
        else:
            print(f"✗ Directory {dir_name}: Missing")
            all_ok = False
    
    return all_ok

def main():
    print("🔍 Online Judge Health Check\n")
    
    checks = [
        ("Database", check_database),
        ("Models", check_models),
        ("Compilers", check_compilers),
        ("Directories", check_directories)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name} Check:")
        if not check_func():
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 All checks passed! System is healthy.")
        sys.exit(0)
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()