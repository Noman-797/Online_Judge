#!/usr/bin/env python3
"""
Quick security fixes for PythonAnywhere deployment
Run this before deploying to fix critical security issues
"""

import os
import re

def fix_settings():
    """Fix critical settings.py issues"""
    settings_path = 'Online_Judge/settings.py'
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Fix DEBUG setting for production
    content = re.sub(
        r'DEBUG = True',
        'DEBUG = False',
        content
    )
    
    # Add security headers
    security_settings = """
# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
"""
    
    if 'SECURE_BROWSER_XSS_FILTER' not in content:
        content += security_settings
    
    with open(settings_path, 'w') as f:
        f.write(content)
    
    print("✓ Settings.py security fixes applied")

def add_auth_decorators():
    """Add basic authentication decorators to views"""
    
    # Fix contests/views.py
    contests_views = 'contests/views.py'
    if os.path.exists(contests_views):
        with open(contests_views, 'r') as f:
            content = f.read()
        
        # Add login_required import
        if 'from django.contrib.auth.decorators import login_required' not in content:
            content = content.replace(
                'from django.shortcuts import render',
                'from django.shortcuts import render\nfrom django.contrib.auth.decorators import login_required'
            )
        
        # Add @login_required to critical views
        content = re.sub(
            r'def (create_contest|edit_contest|delete_contest)',
            r'@login_required\ndef \1',
            content
        )
        
        with open(contests_views, 'w') as f:
            f.write(content)
        
        print("✓ Contest views authentication added")

def fix_xss_issues():
    """Add basic XSS protection"""
    
    # Add to templates - basic escaping
    template_dirs = ['templates']
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        filepath = os.path.join(root, file)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Replace unsafe {{ }} with |escape
                        content = re.sub(
                            r'\{\{\s*([^|}\s]+)\s*\}\}',
                            r'{{ \1|escape }}',
                            content
                        )
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
    
    print("✓ Basic XSS protection added to templates")

if __name__ == '__main__':
    print("Applying critical security fixes for PythonAnywhere deployment...")
    
    fix_settings()
    add_auth_decorators()
    fix_xss_issues()
    
    print("\n✓ Critical fixes applied!")
    print("\nNext steps:")
    print("1. Test locally: python manage.py runserver")
    print("2. Upload to PythonAnywhere")
    print("3. Run migrations: python manage.py migrate")
    print("4. Create superuser: python manage.py createsuperuser")