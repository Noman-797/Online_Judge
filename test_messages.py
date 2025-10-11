#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from django.contrib.auth.models import User
from communications.models import AdminMessage, BroadcastMessage

# Create a test admin message
try:
    user = User.objects.get(username='student')  # or any existing user
    admin = User.objects.filter(is_staff=True).first()
    
    if admin:
        # Create test admin message
        AdminMessage.objects.create(
            user=user,
            admin=admin,
            subject="Test Message",
            message="This is a test message to check bell notification",
            is_from_admin=True,
            is_read=False
        )
        print("Test admin message created!")
        
        # Create test broadcast message
        BroadcastMessage.objects.create(
            admin=admin,
            subject="Test Announcement",
            message="This is a test announcement"
        )
        print("Test broadcast message created!")
        
    else:
        print("No admin user found")
        
except User.DoesNotExist:
    print("Student user not found")

# Check current messages
print("\nCurrent AdminMessages:")
for msg in AdminMessage.objects.all()[:5]:
    print(f"- {msg.subject} (from_admin: {msg.is_from_admin}, read: {msg.is_read})")

print("\nCurrent BroadcastMessages:")
for msg in BroadcastMessage.objects.all()[:5]:
    print(f"- {msg.subject}")