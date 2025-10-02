#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from contests.models import Contest, ContestProblem
from problems.models import Problem, TestCase, Category

def create_test_contest():
    print("Creating test contest...")
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='ojadmin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('OJAdmin2024!')
        admin_user.save()
        print("Created admin user")
    
    # Create a test contest
    contest, created = Contest.objects.get_or_create(
        slug='test-contest-2024',
        defaults={
            'title': 'Test Contest 2024',
            'description': 'A test contest for debugging',
            'rules': 'Standard ACM ICPC rules',
            'start_time': timezone.now() - timedelta(hours=1),  # Started 1 hour ago
            'end_time': timezone.now() + timedelta(hours=2),    # Ends in 2 hours
            'duration': 180,  # 3 hours
            'created_by': admin_user,
            'is_active': True
        }
    )
    if created:
        print(f"Created contest: {contest.title}")
    
    # Get or create a category
    category, created = Category.objects.get_or_create(
        name='Contest Problems',
        defaults={'description': 'Problems for contests'}
    )
    
    # Create a simple test problem
    problem, created = Problem.objects.get_or_create(
        slug='contest-hello-world',
        defaults={
            'title': 'Contest Hello World',
            'description': '<p>Print "Hello World" to the console.</p>',
            'input_format': '<p>No input required.</p>',
            'output_format': '<p>Print "Hello World" (without quotes).</p>',
            'sample_input': '',
            'sample_output': 'Hello World',
            'difficulty': 'Easy',
            'time_limit': 1.0,
            'memory_limit': 256,
            'category': category,
            'created_by': admin_user,
            'contest_only': True,  # Mark as contest only
            'is_active': True
        }
    )
    if created:
        print(f"Created problem: {problem.title}")
        
        # Create test cases
        TestCase.objects.create(
            problem=problem,
            input_data='',
            expected_output='Hello World',
            is_sample=True
        )
        TestCase.objects.create(
            problem=problem,
            input_data='',
            expected_output='Hello World',
            is_sample=False
        )
        print("Created test cases")
    
    # Add problem to contest
    contest_problem, created = ContestProblem.objects.get_or_create(
        contest=contest,
        problem=problem,
        defaults={
            'order': 1,
            'points': 100
        }
    )
    if created:
        print(f"Added problem to contest")
    
    print(f"\nTest contest setup complete!")
    print(f"Contest URL: http://127.0.0.1:8000/contests/{contest.slug}/")
    print(f"Problem URL: http://127.0.0.1:8000/contests/{contest.slug}/problem/{problem.slug}/")
    print(f"Admin login: ojadmin / OJAdmin2024!")

if __name__ == '__main__':
    create_test_contest()