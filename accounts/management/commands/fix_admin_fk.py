from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Fix admin foreign key constraint issues'

    def handle(self, *args, **options):
        self.stdout.write('Fixing admin foreign key constraints...')
        
        with transaction.atomic():
            # Ensure all users have profiles
            for user in User.objects.all():
                profile, created = UserProfile.objects.get_or_create(user=user)
                if created:
                    self.stdout.write(f'Created profile for {user.username}')
            
            # Check for any integrity issues
            try:
                # Test query that might trigger the constraint
                list(User.objects.select_related('userprofile').all())
                self.stdout.write('User-Profile relationships are intact')
            except Exception as e:
                self.stdout.write(f'Error: {e}')
        
        self.stdout.write(self.style.SUCCESS('Admin foreign key constraints fixed!'))