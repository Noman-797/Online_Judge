import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from problems.models import Problem

def restore_contest_problems():
    # Make contest problems contest-only again
    contest_problems = Problem.objects.filter(slug__in=['hello-world', 'sum-two-numbers'])
    
    for problem in contest_problems:
        problem.contest_only = True
        problem.save()
        print(f"Made contest-only: {problem.title}")
    
    print(f"Restored {contest_problems.count()} contest problems")

if __name__ == '__main__':
    restore_contest_problems()