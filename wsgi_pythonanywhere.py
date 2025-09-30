#!/usr/bin/python3.13

import os
import sys

# Add your project directory to the Python path
project_home = '/home/aasoj/Online_Judge'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add user packages path for mysqlclient
sys.path.insert(0, '/home/aasoj/.local/lib/python3.13/site-packages')

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'Online_Judge.settings'
os.environ['PYTHONANYWHERE_DOMAIN'] = '1'

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
