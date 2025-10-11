import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from problems.models import Problem, Category, TestCase
from django.contrib.auth.models import User

admin_user = User.objects.filter(is_staff=True).first()
easy_cat, _ = Category.objects.get_or_create(name='Easy', defaults={'description': 'Easy problems'})
medium_cat, _ = Category.objects.get_or_create(name='Medium', defaults={'description': 'Medium problems'})
hard_cat, _ = Category.objects.get_or_create(name='Hard', defaults={'description': 'Hard problems'})

new_problems = [
    {
        'title': 'Simple Calculator',
        'description': 'Create a calculator that performs basic arithmetic operations.',
        'input_format': 'Three inputs: number1, operator (+, -, *, /), number2',
        'output_format': 'Result of the operation',
        'sample_input': '10 + 5',
        'sample_output': '15',
        'category': easy_cat,
        'test_cases': [('10 + 5', '15'), ('20 - 8', '12'), ('6 * 7', '42'), ('15 / 3', '5')]
    },
    {
        'title': 'Vowel Counter',
        'description': 'Count the number of vowels in a given string.',
        'input_format': 'A string of characters',
        'output_format': 'Number of vowels',
        'sample_input': 'hello world',
        'sample_output': '3',
        'category': easy_cat,
        'test_cases': [('hello world', '3'), ('programming', '3'), ('xyz', '0'), ('aeiou', '5')]
    },
    {
        'title': 'Temperature Converter',
        'description': 'Convert temperature from Celsius to Fahrenheit.',
        'input_format': 'Temperature in Celsius',
        'output_format': 'Temperature in Fahrenheit',
        'sample_input': '25',
        'sample_output': '77',
        'category': easy_cat,
        'test_cases': [('25', '77'), ('0', '32'), ('100', '212'), ('-40', '-40')]
    },
    {
        'title': 'Leap Year Check',
        'description': 'Check if a given year is a leap year.',
        'input_format': 'A year (integer)',
        'output_format': 'Yes if leap year, No otherwise',
        'sample_input': '2020',
        'sample_output': 'Yes',
        'category': medium_cat,
        'test_cases': [('2020', 'Yes'), ('2021', 'No'), ('2000', 'Yes'), ('1900', 'No')]
    },
    {
        'title': 'Reverse Array',
        'description': 'Reverse the elements of an array.',
        'input_format': 'First line: n (size), Second line: n integers',
        'output_format': 'Array elements in reverse order',
        'sample_input': '5\n1 2 3 4 5',
        'sample_output': '5 4 3 2 1',
        'category': medium_cat,
        'test_cases': [('5\n1 2 3 4 5', '5 4 3 2 1'), ('3\n10 20 30', '30 20 10')]
    },
    {
        'title': 'Perfect Number',
        'description': 'Check if a number is perfect (sum of divisors equals the number).',
        'input_format': 'A positive integer',
        'output_format': 'Perfect if perfect number, Not Perfect otherwise',
        'sample_input': '6',
        'sample_output': 'Perfect',
        'category': medium_cat,
        'test_cases': [('6', 'Perfect'), ('28', 'Perfect'), ('12', 'Not Perfect'), ('1', 'Not Perfect')]
    },
    {
        'title': 'Binary to Decimal',
        'description': 'Convert a binary number to decimal.',
        'input_format': 'A binary number (string of 0s and 1s)',
        'output_format': 'Decimal equivalent',
        'sample_input': '1010',
        'sample_output': '10',
        'category': hard_cat,
        'test_cases': [('1010', '10'), ('1111', '15'), ('1000', '8'), ('101', '5')]
    },
    {
        'title': 'Sorting Algorithm',
        'description': 'Sort an array in ascending order.',
        'input_format': 'First line: n, Second line: n integers',
        'output_format': 'Sorted array',
        'sample_input': '5\n64 34 25 12 22',
        'sample_output': '12 22 25 34 64',
        'category': hard_cat,
        'test_cases': [('5\n64 34 25 12 22', '12 22 25 34 64'), ('3\n3 1 2', '1 2 3')]
    },
    {
        'title': 'String Reversal',
        'description': 'Reverse a given string.',
        'input_format': 'A string',
        'output_format': 'Reversed string',
        'sample_input': 'hello',
        'sample_output': 'olleh',
        'category': easy_cat,
        'test_cases': [('hello', 'olleh'), ('world', 'dlrow'), ('a', 'a'), ('abc', 'cba')]
    },
    {
        'title': 'Power Calculator',
        'description': 'Calculate base raised to the power of exponent.',
        'input_format': 'Two integers: base and exponent',
        'output_format': 'Result of base^exponent',
        'sample_input': '2 3',
        'sample_output': '8',
        'category': medium_cat,
        'test_cases': [('2 3', '8'), ('5 2', '25'), ('3 0', '1'), ('10 1', '10')]
    }
]

print("Creating 10 new sample problems...")
created_count = 0

for i, problem_data in enumerate(new_problems, 1):
    if Problem.objects.filter(title=problem_data['title']).exists():
        print(f"Problem {i}: {problem_data['title']} already exists, skipping...")
        continue
        
    problem = Problem.objects.create(
        title=problem_data['title'],
        description=problem_data['description'],
        input_format=problem_data['input_format'],
        output_format=problem_data['output_format'],
        sample_input=problem_data['sample_input'],
        sample_output=problem_data['sample_output'],
        category=problem_data['category'],
        time_limit=1,
        memory_limit=256,
        created_by=admin_user
    )
    
    for j, (input_data, expected_output) in enumerate(problem_data['test_cases']):
        TestCase.objects.create(
            problem=problem,
            input_data=input_data,
            expected_output=expected_output,
            is_sample=(j == 0)
        )
    
    print(f"Created problem {i}: {problem_data['title']}")
    created_count += 1

print(f"\nSuccessfully created {created_count} new problems!")
print(f"Total problems in database: {Problem.objects.count()}")