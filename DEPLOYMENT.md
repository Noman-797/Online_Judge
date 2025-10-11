# PythonAnywhere Deployment Guide

## Prerequisites
- PythonAnywhere account (Hacker plan or higher for MySQL)
- Git repository with your code

## Step 1: Upload Code
1. Open a Bash console on PythonAnywhere
2. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/Online_Judge.git
   cd Online_Judge
   ```

## Step 2: Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 onlinejudge
pip install -r requirements.txt
```

## Step 3: Database Setup
1. Go to PythonAnywhere Dashboard > Databases
2. Create a MySQL database (e.g., `yourusername$default`)
3. Note down the database details

## Step 4: Environment Variables
Create `.env` file in project root:
```bash
SECRET_KEY=your-very-long-secret-key-here
DEBUG=False
DB_NAME=yourusername$default
DB_USER=yourusername
DB_PASSWORD=your-database-password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
PYTHONANYWHERE_DOMAIN=yourusername.pythonanywhere.com
```

## Step 5: Django Setup
```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

## Step 6: Web App Configuration
1. Go to PythonAnywhere Dashboard > Web
2. Create new web app (Manual configuration, Python 3.10)
3. Set source code: `/home/yourusername/Online_Judge`
4. Set working directory: `/home/yourusername/Online_Judge`
5. Edit WSGI file:
   ```python
   import os
   import sys
   
   path = '/home/yourusername/Online_Judge'
   if path not in sys.path:
       sys.path.insert(0, path)
   
   os.environ['DJANGO_SETTINGS_MODULE'] = 'Online_Judge.settings'
   
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

## Step 7: Static Files
1. In Web tab, set static files:
   - URL: `/static/`
   - Directory: `/home/yourusername/Online_Judge/staticfiles/`

## Step 8: Install Compilers (if needed)
For C/C++ support, compilers should already be available on PythonAnywhere.
Test with:
```bash
gcc --version
g++ --version
```

## Step 9: Create Sample Data (Optional)
```bash
python manage.py shell
```
Then create some sample problems and test cases.

## Step 10: Test
1. Reload your web app
2. Visit your site: `https://yourusername.pythonanywhere.com`
3. Test registration, login, and problem submission

## Troubleshooting

### Common Issues:
1. **Import errors**: Check virtual environment activation
2. **Database errors**: Verify database credentials in `.env`
3. **Static files not loading**: Run `collectstatic` and check static files mapping
4. **Compilation errors**: Ensure GCC/G++ are available

### Logs:
- Error logs: PythonAnywhere Dashboard > Web > Log files
- Server logs: `/var/log/yourusername.pythonanywhere.com.server.log`

### Performance Tips:
1. Use database indexing (already implemented)
2. Enable manual queue processing for contests
3. Limit code size (50KB implemented)
4. Set appropriate time limits (2s implemented)

## Security Notes:
- Never commit `.env` file
- Use strong SECRET_KEY
- Keep DEBUG=False in production
- Regularly update dependencies