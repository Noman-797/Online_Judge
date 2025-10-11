import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from problems.models import Problem, Category, TestCase
from django.contrib.auth.models import User

# Get or create admin user
admin_user = User.objects.filter(is_staff=True).first()
if not admin_user:
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

# Get or create categories
easy_cat, _ = Category.objects.get_or_create(name='Easy', defaults={'description': 'Easy problems'})
medium_cat, _ = Category.objects.get_or_create(name='Medium', defaults={'description': 'Medium problems'})
hard_cat, _ = Category.objects.get_or_create(name='Hard', defaults={'description': 'Hard problems'})

problems_data = [
    {
        'title': 'Add Two Numbers',
        'description': 'Write a program that reads two integers and prints their sum.',
        'input_format': 'Two integers a and b on a single line.',
        'output_format': 'Print the sum of a and b.',
        'sample_input': '5 3',
        'sample_output': '8',
        'category': easy_cat,
        'time_limit': 1,
        'memory_limit': 256,
        'test_cases': [
            ('5 3', '8'),
            ('10 20', '30'),
            ('-5 10', '5'),
            ('0 0', '0'),
            ('100 200', '300')
        ]
    },
    {
        'title': 'Even or Odd',
        'description': 'Determine if a given number is even or odd.',
        'input_format': 'A single integer n.',
        'output_format': 'Print "Even" if n is even, "Odd" if n is odd.',
        'sample_input': '4',
        'sample_output': 'Even',
        'category': easy_cat,
        'time_limit': 1,
        'memory_limit': 256,
        'test_cases': [
            ('4', 'Even'),
            ('7', 'Odd'),
            ('0', 'Even'),
            ('1', 'Odd'),
            ('100', 'Even')
        ]
    },
    {
        'title': 'Count Digits',
        'description': 'Count the number of digits in a given integer.',
        'input_format': 'A single integer n.',
        'output_format': 'Print the number of digits in n.',
        'sample_input': '12345',
        'sample_output': '5',
        'category': easy_cat,
        'time_limit': 1,
        'memory_limit': 256,
        'test_cases': [
            ('12345', '5'),
            ('0', '1'),
            ('999', '3'),
            ('1', '1'),
            ('1000000', '7')
        ]
    },
    {
        'title': 'Prime Check',
        'description': 'Check if a given number is prime.',
        'input_format': 'A single integer n (2 ≤ n ≤ 1000).',
        'output_format': 'Print "Prime" if n is prime, "Not Prime" otherwise.',
        'sample_input': '7',
        'sample_output': 'Prime',
        'category': medium_cat,
        'time_limit': 1,
        'memory_limit': 256,
        'test_cases': [
            ('7', 'Prime'),
            ('4', 'Not Prime'),
            ('2', 'Prime'),
            ('100', 'Not Prime'),
            ('97', 'Prime')
        ]
    },
    {
        'title': 'Fibonacci Sequence',
        'description': 'Print the first n numbers of the Fibonacci sequence.',
        'input_format': 'A single integer n (1 ≤ n ≤ 20).',
        'output_format': 'Print the first n Fibonacci numbers separated by spaces.',
        'sample_input': '5',
        'sample_output': '0 1 1 2 3',
        'category': medium_cat,
        'time_limit': 1,
        'memory_limit': 256,
        'test_cases': [
            ('5', '0 1 1 2 3'),
            ('1', '0'),
            ('2', '0 1'),
            ('8', '0 1 1 2 3 5 8 13'),
            ('10', '0 1 1 2 3 5 8 13 21 34')
        ]
    },
    {
        'title': 'Array Sum',
        'description': 'Calculate the sum of all elements in an array.',
        'input_format': 'First line: integer n (size of array)\nSecond line: n integers separated by spaces.',
        'output_format': 'Print the sum of all elements.',
        'sample_input': '5\n1 2 3 4 5',
        'sample_output': '15',
        'category': easy_cat,
        'time_limit': 1,
        'memory_limit': 256,
        'test_cases': [
            ('5\n1 2 3 4 5', '15'),
            ('3\n10 20 30', '60'),
            ('1\n100', '100'),
            ('4\n-1 -2 -3 -4', '-10'),
            ('6\n0 0 0 0 0 0', '0')
        ]
    },
    {
        'title': 'Palindrome Check',
        'description': 'Check if a given string is a palindrome.',
        'input_format': 'A single string s.',
        'output_format': 'Print "Yes" if s is a palindrome, "No" otherwise.',
        'sample_input': 'racecar',
        'sample_output': 'Yes',
        'category': medium_cat,
        'time_limit': 1,
        'memory_limit': 256,
        'test_cases': [
            ('racecar', 'Yes'),
            ('hello', 'No'),
            ('a', 'Yes'),
            ('abba', 'Yes'),
            ('abc', 'No')
        ]
    },
    {
        'title': 'Binary Search',
        'description': 'Implement binary search to find an element in a sorted array.',
        'input_format': 'First line: n (array size) and x (element to find)\nSecond line: n sorted integers.',
        'output_format': 'Print the index (0-based) if found, -1 otherwise.',
        'sample_input': '5 3\n1 2 3 4 5',
        'sample_output': '2',
        'category': hard_cat,
        'time_limit': 1,
        'memory_limit': 256,
        'test_cases': [
            ('5 3\n1 2 3 4 5', '2'),
            ('5 6\n1 2 3 4 5', '-1'),
            ('1 1\n1', '0'),
            ('4 2\n1 2 3 4', '1'),
            ('3 5\n1 3 5', '2')
        ]
    },
    {
        'title': 'GCD Calculator',
        'description': 'Find the Greatest Common Divisor (GCD) of two numbers.',
        'input_format': 'Two integers a and b.',
        'output_format': 'Print the GCD of a and b.',
        'sample_input': '12 18',
        'sample_output': '6',
        'category': medium_cat,
        'time_limit': 1,
        'memory_limit': 256,
        'test_cases': [
            ('12 18', '6'),
            ('7 13', '1'),
            ('100 50', '50'),
            ('48 18', '6'),
            ('17 19', '1')
        ]
    },
    {
        'title': 'Matrix Multiplication',
        'description': 'Multiply two 2x2 matrices.',
        'input_format': 'First matrix: 2 lines with 2 integers each\nSecond matrix: 2 lines with 2 integers each',
        'output_format': 'Print the resulting 2x2 matrix.',
        'sample_input': '1 2\n3 4\n5 6\n7 8',
        'sample_output': '19 22\n43 50',
        'category': hard_cat,
        'time_limit': 1,
        'memory_limit': 256,
        'test_cases': [
            ('1 2\n3 4\n5 6\n7 8', '19 22\n43 50'),
            ('1 0\n0 1\n2 3\n4 5', '2 3\n4 5'),
            ('2 1\n1 2\n1 1\n1 1', '3 3\n3 3'),
            ('0 1\n1 0\n1 2\n3 4', '3 4\n1 2'),
            ('1 1\n1 1\n2 2\n2 2', '4 4\n4 4')
        ]
    }
]

print("Creating 10 sample problems...")

for i, problem_data in enumerate(problems_data, 1):
    # Check if problem already exists
    if Problem.objects.filter(title=problem_data['title']).exists():
        print(f"Problem {i}: {problem_data['title']} already exists, skipping...")
        continue
        
    # Create problem
    problem = Problem.objects.create(
        title=problem_data['title'],
        description=problem_data['description'],
        input_format=problem_data['input_format'],
        output_format=problem_data['output_format'],
        sample_input=problem_data['sample_input'],
        sample_output=problem_data['sample_output'],
        category=problem_data['category'],
        time_limit=problem_data['time_limit'],
        memory_limit=problem_data['memory_limit'],
        created_by=admin_user
    )
    
    # Create test cases
    for j, (input_data, expected_output) in enumerate(problem_data['test_cases']):
        TestCase.objects.create(
            problem=problem,
            input_data=input_data,
            expected_output=expected_output,
            is_sample=(j == 0)  # First test case is sample
        )
    
    print(f"Created problem {i}: {problem_data['title']}")

print(f"\nSuccessfully created {len(problems_data)} sample problems!")
print("Categories created:")
print(f"- Easy: {Problem.objects.filter(category=easy_cat).count()} problems")
print(f"- Medium: {Problem.objects.filter(category=medium_cat).count()} problems") 
print(f"- Hard: {Problem.objects.filter(category=hard_cat).count()} problems")