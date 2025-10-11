import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

from problems.models import Problem, Category, TestCase
from django.contrib.auth.models import User

admin_user = User.objects.filter(is_staff=True).first()
easy_cat, _ = Category.objects.get_or_create(name='Easy', defaults={'description': 'Easy problems'})
medium_cat, _ = Category.objects.get_or_create(name='Medium', defaults={'description': 'Medium problems'})

problems = [
    ('Calculator App', 'Create a calculator for basic operations.', '10 + 5', '15', easy_cat),
    ('Count Vowels', 'Count vowels in a string.', 'hello', '2', easy_cat),
    ('Temperature Convert', 'Convert Celsius to Fahrenheit.', '25', '77', easy_cat),
    ('Year Checker', 'Check if year is leap year.', '2020', 'Yes', medium_cat),
    ('Array Reverse', 'Reverse array elements.', '5\n1 2 3 4 5', '5 4 3 2 1', medium_cat),
    ('Perfect Check', 'Check if number is perfect.', '6', 'Perfect', medium_cat),
    ('Binary Convert', 'Convert binary to decimal.', '1010', '10', medium_cat),
    ('Sort Numbers', 'Sort array in ascending order.', '5\n64 34 25 12 22', '12 22 25 34 64', medium_cat),
    ('Reverse Text', 'Reverse a string.', 'hello', 'olleh', easy_cat),
    ('Power Math', 'Calculate base^exponent.', '2 3', '8', medium_cat)
]

print("Creating problems with unique slugs...")
created = 0

for i, (title, desc, sample_in, sample_out, category) in enumerate(problems):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    # Ensure unique slug
    while Problem.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    if Problem.objects.filter(title=title).exists():
        print(f"Problem '{title}' already exists, skipping...")
        continue
    
    problem = Problem.objects.create(
        title=title,
        slug=slug,
        description=desc,
        input_format='Standard input format',
        output_format='Standard output format',
        sample_input=sample_in,
        sample_output=sample_out,
        difficulty=category.name,
        category=category,
        time_limit=1,
        memory_limit=256,
        created_by=admin_user
    )
    
    # Add basic test cases
    TestCase.objects.create(
        problem=problem,
        input_data=sample_in,
        expected_output=sample_out,
        is_sample=True
    )
    
    print(f"Created: {title} (slug: {slug})")
    created += 1

print(f"\nCreated {created} new problems!")
print(f"Total problems: {Problem.objects.count()}")