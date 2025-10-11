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
    user = User.objects.get(username='nomancsediu')  # non-staff user
    admin = User.objects.get(username='nomancse')    # staff user
    
    # Create test admin message
    AdminMessage.objects.create(
        user=user,
        admin=admin,
        subject="Test Bell Notification",
        message="This is a test message to check if bell notification works",
        is_from_admin=True,
        is_read=False
    )
    print("Test admin message created for nomancsediu!")
    
    # Create test broadcast message
    BroadcastMessage.objects.create(
        admin=admin,
        subject="Test Announcement Bell",
        message="This is a test announcement for bell notification"
    )
    print("Test broadcast message created!")
        
except User.DoesNotExist as e:
    print(f"User not found: {e}")

print("\nUnread messages for nomancsediu:")
unread = AdminMessage.objects.filter(
    user__username='nomancsediu',
    is_from_admin=True,
    is_read=False
).count()
print(f"Count: {unread}")