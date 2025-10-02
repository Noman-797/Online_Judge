import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from problems.models import Problem, Category, TestCase
from contests.models import Contest, ContestProblem
from django.contrib.auth.models import User

def create_problems_and_contest():
    # Get or create admin user
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Create categories
    basic_cat, _ = Category.objects.get_or_create(name="Basic Programming")
    math_cat, _ = Category.objects.get_or_create(name="Mathematics")
    string_cat, _ = Category.objects.get_or_create(name="String Processing")
    array_cat, _ = Category.objects.get_or_create(name="Array & Sorting")
    
    problems_data = [
        # Basic Problems (1-5)
        {
            'title': 'Hello World',
            'slug': 'hello-world',
            'description': 'Print "Hello, World!" to the console.',
            'input_format': 'No input required.',
            'output_format': 'Print "Hello, World!" exactly.',
            'category': basic_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('', 'Hello, World!')
            ]
        },
        {
            'title': 'Sum of Two Numbers',
            'slug': 'sum-two-numbers',
            'description': 'Given two integers, print their sum.',
            'input_format': 'Two integers A and B separated by space.',
            'output_format': 'Print the sum A + B.',
            'category': basic_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('5 3', '8'),
                ('10 20', '30'),
                ('-5 15', '10')
            ]
        },
        {
            'title': 'Even or Odd',
            'slug': 'even-or-odd',
            'description': 'Check if a number is even or odd.',
            'input_format': 'One integer N.',
            'output_format': 'Print "Even" if N is even, "Odd" if N is odd.',
            'category': basic_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('4', 'Even'),
                ('7', 'Odd'),
                ('0', 'Even')
            ]
        },
        {
            'title': 'Maximum of Three',
            'slug': 'max-of-three',
            'description': 'Find the maximum of three numbers.',
            'input_format': 'Three integers A, B, C separated by spaces.',
            'output_format': 'Print the maximum number.',
            'category': basic_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('5 3 8', '8'),
                ('10 10 5', '10'),
                ('-1 -5 -3', '-1')
            ]
        },
        {
            'title': 'Simple Calculator',
            'slug': 'simple-calculator',
            'description': 'Perform basic arithmetic operations.',
            'input_format': 'Two integers A, B and an operator (+, -, *, /).',
            'output_format': 'Print the result of A operator B.',
            'category': basic_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('10 5 +', '15'),
                ('10 5 -', '5'),
                ('10 5 *', '50')
            ]
        },
        
        # Math Problems (6-10)
        {
            'title': 'Factorial',
            'slug': 'factorial',
            'description': 'Calculate the factorial of a number.',
            'input_format': 'One integer N (0 ≤ N ≤ 10).',
            'output_format': 'Print N! (factorial of N).',
            'category': math_cat,
            'difficulty': 'Medium',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('5', '120'),
                ('0', '1'),
                ('3', '6')
            ]
        },
        {
            'title': 'Prime Check',
            'slug': 'prime-check',
            'description': 'Check if a number is prime.',
            'input_format': 'One integer N (N > 1).',
            'output_format': 'Print "Prime" if N is prime, "Not Prime" otherwise.',
            'category': math_cat,
            'difficulty': 'Medium',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('7', 'Prime'),
                ('4', 'Not Prime'),
                ('13', 'Prime')
            ]
        },
        {
            'title': 'GCD of Two Numbers',
            'slug': 'gcd-two-numbers',
            'description': 'Find the Greatest Common Divisor of two numbers.',
            'input_format': 'Two integers A and B.',
            'output_format': 'Print GCD(A, B).',
            'category': math_cat,
            'difficulty': 'Medium',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('12 8', '4'),
                ('15 25', '5'),
                ('7 13', '1')
            ]
        },
        {
            'title': 'Fibonacci Sequence',
            'slug': 'fibonacci',
            'description': 'Print the Nth Fibonacci number.',
            'input_format': 'One integer N (1 ≤ N ≤ 20).',
            'output_format': 'Print the Nth Fibonacci number.',
            'category': math_cat,
            'difficulty': 'Medium',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('1', '1'),
                ('5', '5'),
                ('8', '21')
            ]
        },
        {
            'title': 'Power Calculation',
            'slug': 'power-calculation',
            'description': 'Calculate A raised to the power B.',
            'input_format': 'Two integers A and B.',
            'output_format': 'Print A^B.',
            'category': math_cat,
            'difficulty': 'Medium',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('2 3', '8'),
                ('5 2', '25'),
                ('3 0', '1')
            ]
        },
        
        # String Problems (11-15)
        {
            'title': 'String Length',
            'slug': 'string-length',
            'description': 'Find the length of a string.',
            'input_format': 'One string S.',
            'output_format': 'Print the length of string S.',
            'category': string_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('hello', '5'),
                ('programming', '11'),
                ('a', '1')
            ]
        },
        {
            'title': 'Reverse String',
            'slug': 'reverse-string',
            'description': 'Reverse a given string.',
            'input_format': 'One string S.',
            'output_format': 'Print the reversed string.',
            'category': string_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('hello', 'olleh'),
                ('abc', 'cba'),
                ('programming', 'gnimmargorp')
            ]
        },
        {
            'title': 'Palindrome Check',
            'slug': 'palindrome-check',
            'description': 'Check if a string is a palindrome.',
            'input_format': 'One string S.',
            'output_format': 'Print "Yes" if palindrome, "No" otherwise.',
            'category': string_cat,
            'difficulty': 'Medium',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('racecar', 'Yes'),
                ('hello', 'No'),
                ('madam', 'Yes')
            ]
        },
        {
            'title': 'Count Vowels',
            'slug': 'count-vowels',
            'description': 'Count the number of vowels in a string.',
            'input_format': 'One string S.',
            'output_format': 'Print the count of vowels.',
            'category': string_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('hello', '2'),
                ('programming', '3'),
                ('xyz', '0')
            ]
        },
        {
            'title': 'String Comparison',
            'slug': 'string-comparison',
            'description': 'Compare two strings lexicographically.',
            'input_format': 'Two strings A and B.',
            'output_format': 'Print "A" if A < B, "B" if B < A, "Equal" if equal.',
            'category': string_cat,
            'difficulty': 'Medium',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('apple banana', 'A'),
                ('cat dog', 'A'),
                ('hello hello', 'Equal')
            ]
        },
        
        # Array Problems (16-20)
        {
            'title': 'Array Sum',
            'slug': 'array-sum',
            'description': 'Calculate the sum of array elements.',
            'input_format': 'First line: N (array size). Second line: N integers.',
            'output_format': 'Print the sum of all elements.',
            'category': array_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('3\n1 2 3', '6'),
                ('5\n10 20 30 40 50', '150'),
                ('1\n42', '42')
            ]
        },
        {
            'title': 'Find Maximum',
            'slug': 'find-maximum',
            'description': 'Find the maximum element in an array.',
            'input_format': 'First line: N (array size). Second line: N integers.',
            'output_format': 'Print the maximum element.',
            'category': array_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('3\n1 5 3', '5'),
                ('4\n-1 -5 -2 -8', '-1'),
                ('1\n42', '42')
            ]
        },
        {
            'title': 'Array Average',
            'slug': 'array-average',
            'description': 'Calculate the average of array elements.',
            'input_format': 'First line: N (array size). Second line: N integers.',
            'output_format': 'Print the average (rounded to 2 decimal places).',
            'category': array_cat,
            'difficulty': 'Medium',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('3\n1 2 3', '2.00'),
                ('4\n10 20 30 40', '25.00'),
                ('2\n5 7', '6.00')
            ]
        },
        {
            'title': 'Bubble Sort',
            'slug': 'bubble-sort',
            'description': 'Sort an array using bubble sort algorithm.',
            'input_format': 'First line: N (array size). Second line: N integers.',
            'output_format': 'Print the sorted array elements separated by spaces.',
            'category': array_cat,
            'difficulty': 'Medium',
            'time_limit': 2,
            'memory_limit': 64,
            'test_cases': [
                ('5\n64 34 25 12 22', '12 22 25 34 64'),
                ('3\n3 1 2', '1 2 3'),
                ('1\n42', '42')
            ]
        },
        {
            'title': 'Search Element',
            'slug': 'search-element',
            'description': 'Search for an element in an array.',
            'input_format': 'First line: N (array size). Second line: N integers. Third line: X (element to search).',
            'output_format': 'Print "Found" if element exists, "Not Found" otherwise.',
            'category': array_cat,
            'difficulty': 'Easy',
            'time_limit': 1,
            'memory_limit': 64,
            'test_cases': [
                ('5\n1 2 3 4 5\n3', 'Found'),
                ('3\n10 20 30\n15', 'Not Found'),
                ('1\n42\n42', 'Found')
            ]
        }
    ]
    
    # Create problems
    created_problems = []
    for prob_data in problems_data:
        problem, created = Problem.objects.get_or_create(
            slug=prob_data['slug'],
            defaults={
                'title': prob_data['title'],
                'description': prob_data['description'],
                'input_format': prob_data['input_format'],
                'output_format': prob_data['output_format'],
                'category': prob_data['category'],
                'difficulty': prob_data['difficulty'],
                'time_limit': prob_data['time_limit'],
                'memory_limit': prob_data['memory_limit'],
                'is_active': True,
                'contest_only': False,
                'created_by': admin_user
            }
        )
        
        if created:
            # Create test cases
            for i, (input_data, expected_output) in enumerate(prob_data['test_cases']):
                TestCase.objects.create(
                    problem=problem,
                    input_data=input_data,
                    expected_output=expected_output,
                    is_sample=i == 0  # First test case is sample
                )
            
            created_problems.append(problem)
            print(f"Created problem: {problem.title}")
    
    # Create contest
    contest, created = Contest.objects.get_or_create(
        slug='programming-contest-2024',
        defaults={
            'title': 'Programming Contest 2024',
            'description': 'A beginner-friendly programming contest with 2 problems.',
            'start_time': timezone.now() + timedelta(hours=1),
            'end_time': timezone.now() + timedelta(hours=4),
            'duration': 180,  # 3 hours in minutes
            'is_active': True,
            'created_by': admin_user
        }
    )
    
    if created:
        # Add 2 problems to contest (Hello World and Sum of Two Numbers)
        contest_problems = Problem.objects.filter(slug__in=['hello-world', 'sum-two-numbers'])
        for i, problem in enumerate(contest_problems):
            ContestProblem.objects.create(
                contest=contest,
                problem=problem,
                order=i + 1
            )
            # Mark problems as contest-only
            problem.contest_only = True
            problem.save()
        
        print(f"Created contest: {contest.title} with {contest_problems.count()} problems")
    
    print(f"\nTotal problems created: {len(created_problems)}")
    print("Contest created with 2 problems")

if __name__ == '__main__':
    create_problems_and_contest()