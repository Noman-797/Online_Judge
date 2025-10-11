from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from problems.models import Problem, Category, TestCase
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Create sample problems and test cases'

    def handle(self, *args, **options):
        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user: admin/admin123'))
        else:
            admin = User.objects.get(username='admin')

        # Create categories
        categories_data = [
            ('Basic Programming', 'Fundamental programming concepts'),
            ('Arrays', 'Array manipulation and algorithms'),
            ('Strings', 'String processing problems'),
            ('Mathematics', 'Mathematical computations'),
        ]

        for name, desc in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            if created:
                self.stdout.write(f'Created category: {name}')

        # Create sample problems
        problems_data = [
            {
                'title': 'Hello World',
                'description': 'Print "Hello, World!" to the console.',
                'input_format': 'No input required.',
                'output_format': 'Print "Hello, World!" (without quotes).',
                'sample_input': '',
                'sample_output': 'Hello, World!',
                'difficulty': 'Easy',
                'category': 'Basic Programming',
                'test_cases': [
                    ('', 'Hello, World!')
                ]
            },
            {
                'title': 'Sum of Two Numbers',
                'description': 'Given two integers, find their sum.',
                'input_format': 'Two integers A and B separated by space.',
                'output_format': 'Print the sum of A and B.',
                'sample_input': '5 3',
                'sample_output': '8',
                'difficulty': 'Easy',
                'category': 'Basic Programming',
                'test_cases': [
                    ('5 3', '8'),
                    ('10 20', '30'),
                    ('-5 5', '0'),
                    ('0 0', '0')
                ]
            },
            {
                'title': 'Maximum of Array',
                'description': 'Find the maximum element in an array.',
                'input_format': 'First line contains N (size of array). Second line contains N integers.',
                'output_format': 'Print the maximum element.',
                'sample_input': '5\\n1 3 7 2 5',
                'sample_output': '7',
                'difficulty': 'Easy',
                'category': 'Arrays',
                'test_cases': [
                    ('5\\n1 3 7 2 5', '7'),
                    ('3\\n-1 -5 -2', '-1'),
                    ('1\\n42', '42')
                ]
            }
        ]

        for prob_data in problems_data:
            category = Category.objects.get(name=prob_data['category'])
            
            problem, created = Problem.objects.get_or_create(
                title=prob_data['title'],
                defaults={
                    'slug': slugify(prob_data['title']),
                    'description': prob_data['description'],
                    'input_format': prob_data['input_format'],
                    'output_format': prob_data['output_format'],
                    'sample_input': prob_data['sample_input'],
                    'sample_output': prob_data['sample_output'],
                    'difficulty': prob_data['difficulty'],
                    'category': category,
                    'created_by': admin,
                    'time_limit': 2,
                    'memory_limit': 128
                }
            )
            
            if created:
                self.stdout.write(f'Created problem: {prob_data["title"]}')
                
                # Create test cases
                for i, (inp, out) in enumerate(prob_data['test_cases']):
                    TestCase.objects.create(
                        problem=problem,
                        input_data=inp.replace('\\n', '\n'),
                        expected_output=out,
                        is_sample=(i == 0)
                    )
                
                self.stdout.write(f'  Added {len(prob_data["test_cases"])} test cases')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))