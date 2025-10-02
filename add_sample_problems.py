#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from problems.models import Problem, Category, TestCase
from django.contrib.auth.models import User
from django.utils.text import slugify

def create_sample_problems():
    # Get or create admin user
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    
    # Get or create categories
    categories = {}
    category_names = ['Arrays', 'Strings', 'Math', 'Loops', 'Conditionals', 'Sorting']
    for name in category_names:
        category, created = Category.objects.get_or_create(name=name)
        categories[name] = category
    
    # Sample problems data
    problems_data = [
        {
            'title': 'Two Sum',
            'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
            'input_format': 'First line contains n (size of array) and target. Second line contains n integers.',
            'output_format': 'Print two indices (0-based) that sum to target.',
            'sample_input': '4 9\n2 7 11 15',
            'sample_output': '0 1',
            'difficulty': 'Easy',
            'category': 'Arrays',
            'time_limit': 2
        },
        {
            'title': 'Palindrome Check',
            'description': 'Check if a given string is a palindrome.',
            'input_format': 'A single string.',
            'output_format': 'Print "YES" if palindrome, "NO" otherwise.',
            'sample_input': 'racecar',
            'sample_output': 'YES',
            'difficulty': 'Easy',
            'category': 'Strings',
            'time_limit': 1
        },
        {
            'title': 'Prime Number',
            'description': 'Check if a given number is prime.',
            'input_format': 'A single integer n.',
            'output_format': 'Print "YES" if prime, "NO" otherwise.',
            'sample_input': '17',
            'sample_output': 'YES',
            'difficulty': 'Easy',
            'category': 'Math',
            'time_limit': 1
        },
        {
            'title': 'Fibonacci Sequence',
            'description': 'Print the first n numbers of Fibonacci sequence.',
            'input_format': 'A single integer n.',
            'output_format': 'Print n Fibonacci numbers separated by space.',
            'sample_input': '5',
            'sample_output': '0 1 1 2 3',
            'difficulty': 'Easy',
            'category': 'Math',
            'time_limit': 1
        },
        {
            'title': 'Array Rotation',
            'description': 'Rotate an array to the right by k steps.',
            'input_format': 'First line: n and k. Second line: n integers.',
            'output_format': 'Print the rotated array.',
            'sample_input': '5 2\n1 2 3 4 5',
            'sample_output': '4 5 1 2 3',
            'difficulty': 'Medium',
            'category': 'Arrays',
            'time_limit': 2
        },
        {
            'title': 'Binary Search',
            'description': 'Find the position of target in a sorted array.',
            'input_format': 'First line: n and target. Second line: n sorted integers.',
            'output_format': 'Print the index (0-based) or -1 if not found.',
            'sample_input': '5 3\n1 2 3 4 5',
            'sample_output': '2',
            'difficulty': 'Medium',
            'category': 'Arrays',
            'time_limit': 2
        },
        {
            'title': 'String Reversal',
            'description': 'Reverse each word in a string.',
            'input_format': 'A string with multiple words.',
            'output_format': 'Print the string with each word reversed.',
            'sample_input': 'hello world',
            'sample_output': 'olleh dlrow',
            'difficulty': 'Easy',
            'category': 'Strings',
            'time_limit': 1
        },
        {
            'title': 'Count Vowels',
            'description': 'Count the number of vowels in a string.',
            'input_format': 'A single string.',
            'output_format': 'Print the count of vowels.',
            'sample_input': 'programming',
            'sample_output': '3',
            'difficulty': 'Easy',
            'category': 'Strings',
            'time_limit': 1
        },
        {
            'title': 'GCD Calculator',
            'description': 'Find the Greatest Common Divisor of two numbers.',
            'input_format': 'Two integers a and b.',
            'output_format': 'Print the GCD.',
            'sample_input': '48 18',
            'sample_output': '6',
            'difficulty': 'Easy',
            'category': 'Math',
            'time_limit': 1
        },
        {
            'title': 'Pattern Printing',
            'description': 'Print a pyramid pattern of stars.',
            'input_format': 'A single integer n (height).',
            'output_format': 'Print the pyramid pattern.',
            'sample_input': '3',
            'sample_output': '  *\n ***\n*****',
            'difficulty': 'Easy',
            'category': 'Loops',
            'time_limit': 1
        },
        {
            'title': 'Merge Sort',
            'description': 'Sort an array using merge sort algorithm.',
            'input_format': 'First line: n. Second line: n integers.',
            'output_format': 'Print the sorted array.',
            'sample_input': '5\n5 2 8 1 9',
            'sample_output': '1 2 5 8 9',
            'difficulty': 'Hard',
            'category': 'Sorting',
            'time_limit': 3
        },
        {
            'title': 'Quick Sort',
            'description': 'Sort an array using quick sort algorithm.',
            'input_format': 'First line: n. Second line: n integers.',
            'output_format': 'Print the sorted array.',
            'sample_input': '4\n3 1 4 2',
            'sample_output': '1 2 3 4',
            'difficulty': 'Hard',
            'category': 'Sorting',
            'time_limit': 3
        },
        {
            'title': 'Matrix Multiplication',
            'description': 'Multiply two matrices.',
            'input_format': 'Matrix dimensions and elements.',
            'output_format': 'Print the result matrix.',
            'sample_input': '2 2\n1 2\n3 4\n2 2\n5 6\n7 8',
            'sample_output': '19 22\n43 50',
            'difficulty': 'Medium',
            'category': 'Arrays',
            'time_limit': 2
        },
        {
            'title': 'Longest Substring',
            'description': 'Find the longest substring without repeating characters.',
            'input_format': 'A single string.',
            'output_format': 'Print the length of longest substring.',
            'sample_input': 'abcabcbb',
            'sample_output': '3',
            'difficulty': 'Medium',
            'category': 'Strings',
            'time_limit': 2
        },
        {
            'title': 'Power Calculation',
            'description': 'Calculate a^b mod m efficiently.',
            'input_format': 'Three integers a, b, m.',
            'output_format': 'Print a^b mod m.',
            'sample_input': '2 10 1000',
            'sample_output': '24',
            'difficulty': 'Medium',
            'category': 'Math',
            'time_limit': 2
        },
        {
            'title': 'Even Odd Check',
            'description': 'Check if a number is even or odd.',
            'input_format': 'A single integer.',
            'output_format': 'Print "EVEN" or "ODD".',
            'sample_input': '7',
            'sample_output': 'ODD',
            'difficulty': 'Easy',
            'category': 'Conditionals',
            'time_limit': 1
        },
        {
            'title': 'Sum of Digits',
            'description': 'Calculate the sum of digits of a number.',
            'input_format': 'A single integer.',
            'output_format': 'Print the sum of digits.',
            'sample_input': '123',
            'sample_output': '6',
            'difficulty': 'Easy',
            'category': 'Math',
            'time_limit': 1
        },
        {
            'title': 'Multiplication Table',
            'description': 'Print multiplication table of a number.',
            'input_format': 'A single integer n.',
            'output_format': 'Print table from 1 to 10.',
            'sample_input': '5',
            'sample_output': '5 10 15 20 25 30 35 40 45 50',
            'difficulty': 'Easy',
            'category': 'Loops',
            'time_limit': 1
        },
        {
            'title': 'Anagram Check',
            'description': 'Check if two strings are anagrams.',
            'input_format': 'Two strings on separate lines.',
            'output_format': 'Print "YES" if anagrams, "NO" otherwise.',
            'sample_input': 'listen\nsilent',
            'sample_output': 'YES',
            'difficulty': 'Medium',
            'category': 'Strings',
            'time_limit': 2
        },
        {
            'title': 'Selection Sort',
            'description': 'Sort an array using selection sort.',
            'input_format': 'First line: n. Second line: n integers.',
            'output_format': 'Print the sorted array.',
            'sample_input': '4\n64 25 12 22',
            'sample_output': '12 22 25 64',
            'difficulty': 'Medium',
            'category': 'Sorting',
            'time_limit': 2
        }
    ]
    
    created_count = 0
    for problem_data in problems_data:
        # Check if problem already exists
        if Problem.objects.filter(title=problem_data['title']).exists():
            print(f"Problem '{problem_data['title']}' already exists, skipping...")
            continue
        
        # Create problem
        problem = Problem.objects.create(
            title=problem_data['title'],
            slug=slugify(problem_data['title']),
            description=problem_data['description'],
            input_format=problem_data['input_format'],
            output_format=problem_data['output_format'],
            sample_input=problem_data['sample_input'],
            sample_output=problem_data['sample_output'],
            difficulty=problem_data['difficulty'],
            category=categories[problem_data['category']],
            time_limit=problem_data['time_limit'],
            memory_limit=128,
            created_by=admin_user,
            contest_only=False  # Regular problems, not contest-only
        )
        
        # Create test cases
        TestCase.objects.create(
            problem=problem,
            input_data=problem_data['sample_input'],
            expected_output=problem_data['sample_output'],
            is_sample=True
        )
        
        created_count += 1
        print(f"Created problem: {problem.title}")
    
    print(f"\nSuccessfully created {created_count} sample problems!")

if __name__ == '__main__':
    create_sample_problems()