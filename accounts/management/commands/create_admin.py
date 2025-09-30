import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create admin user with separate credentials'

    def handle(self, *args, **options):
        # Admin credentials
        admin_username = 'ojadmin'
        admin_password = os.environ.get('ADMIN_PASSWORD', 'OJAdmin2024!')
        admin_email = 'admin@onlinejudge.com'

        # Check if admin already exists
        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{admin_username}" already exists')
            )
            return

        # Create admin user
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name='Online Judge',
            last_name='Administrator'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin user: {admin_username}')
        )
        self.stdout.write(f'Username: {admin_username}')
        self.stdout.write(f'Password: {admin_password}')
        self.stdout.write(f'Email: {admin_email}')
        self.stdout.write('')
        self.stdout.write('Admin can access:')
        self.stdout.write('- Django Admin Panel: /admin/')
        self.stdout.write('- All system features')
        self.stdout.write('- User management')
        self.stdout.write('- Problem management')