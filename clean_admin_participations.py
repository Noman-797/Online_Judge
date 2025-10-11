#!/usr/bin/env python
"""
Script to remove admin users from contest participations
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from django.contrib.auth.models import User
from contests.models import ContestParticipation

def clean_admin_participations():
    """Remove admin users from contest participations"""
    
    # Get all admin users (staff or superuser)
    admin_users = User.objects.filter(
        models.Q(is_staff=True) | models.Q(is_superuser=True)
    )
    
    print(f"Found {admin_users.count()} admin users")
    
    # Remove their contest participations
    deleted_count = 0
    for admin_user in admin_users:
        participations = ContestParticipation.objects.filter(user=admin_user)
        count = participations.count()
        if count > 0:
            print(f"Removing {count} participations for admin user: {admin_user.username}")
            participations.delete()
            deleted_count += count
    
    print(f"Total participations removed: {deleted_count}")

if __name__ == '__main__':
    from django.db import models
    clean_admin_participations()