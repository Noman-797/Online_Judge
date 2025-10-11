#!/usr/bin/env python
"""
Test script to verify admin users cannot participate in contests
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from django.contrib.auth.models import User
from contests.models import Contest, ContestParticipation
from django.utils import timezone
from datetime import timedelta

def test_admin_restrictions():
    """Test that admin users cannot participate in contests"""
    
    print("Testing admin contest restrictions...")
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='testadmin',
        defaults={
            'email': 'admin@test.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('testpass')
        admin_user.save()
        print(f"Created admin user: {admin_user.username}")
    else:
        print(f"Using existing admin user: {admin_user.username}")
    
    # Get or create regular user
    regular_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'user@test.com',
            'is_staff': False,
            'is_superuser': False
        }
    )
    if created:
        regular_user.set_password('testpass')
        regular_user.save()
        print(f"Created regular user: {regular_user.username}")
    else:
        print(f"Using existing regular user: {regular_user.username}")
    
    # Create a test contest
    contest, created = Contest.objects.get_or_create(
        slug='test-contest',
        defaults={
            'title': 'Test Contest',
            'description': 'Test contest for admin restrictions',
            'start_time': timezone.now(),
            'end_time': timezone.now() + timedelta(hours=2),
            'duration': 120,
            'created_by': admin_user
        }
    )
    if created:
        print(f"Created test contest: {contest.title}")
    else:
        print(f"Using existing test contest: {contest.title}")
    
    # Test 1: Try to create participation for admin user (should fail)
    print("\nTest 1: Admin user participation")
    try:
        participation = ContestParticipation(contest=contest, user=admin_user)
        participation.save()
        print("❌ FAILED: Admin user was able to participate in contest")
    except ValueError as e:
        print(f"✅ PASSED: Admin user blocked from participation - {e}")
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
    
    # Test 2: Regular user should be able to participate
    print("\nTest 2: Regular user participation")
    try:
        participation = ContestParticipation.objects.get_or_create(
            contest=contest, 
            user=regular_user
        )[0]
        print("✅ PASSED: Regular user can participate in contest")
    except Exception as e:
        print(f"❌ FAILED: Regular user blocked from participation - {e}")
    
    # Test 3: Check leaderboard excludes admin users
    print("\nTest 3: Leaderboard filtering")
    all_participations = ContestParticipation.objects.filter(contest=contest)
    filtered_participations = ContestParticipation.objects.filter(
        contest=contest,
        user__is_staff=False,
        user__is_superuser=False
    )
    
    print(f"Total participations: {all_participations.count()}")
    print(f"Non-admin participations: {filtered_participations.count()}")
    
    admin_in_filtered = filtered_participations.filter(user__is_staff=True).exists()
    if not admin_in_filtered:
        print("✅ PASSED: Admin users excluded from leaderboard query")
    else:
        print("❌ FAILED: Admin users still in leaderboard query")
    
    print("\nTest completed!")

if __name__ == '__main__':
    test_admin_restrictions()