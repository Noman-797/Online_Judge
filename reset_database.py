import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Online_Judge.settings')
django.setup()

def reset_database():
    print("🔄 Resetting database...")
    
    # Try to delete the database file
    db_file = 'db.sqlite3'
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print("✅ Old database deleted")
        except PermissionError:
            print("⚠️  Database file is in use. Please close any Django processes and try again.")
            return False
    
    # Create new migrations
    print("📝 Creating new migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # Apply migrations
    print("🔧 Applying migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Database reset complete!")
    print("👤 Now create a superuser with: python manage.py createsuperuser")
    return True

if __name__ == '__main__':
    reset_database()