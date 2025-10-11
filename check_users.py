#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from django.contrib.auth.models import User
from communications.models import AdminMessage

print("All users:")
for user in User.objects.all():
    print(f"- {user.username} (staff: {user.is_staff})")

print("\nAdminMessages with unread from admin:")
for msg in AdminMessage.objects.filter(is_from_admin=True, is_read=False):
    print(f"- {msg.subject} for {msg.user.username}")