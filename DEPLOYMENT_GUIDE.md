# PythonAnywhere Deployment Guide

## Prerequisites
- PythonAnywhere account (free or paid)
- Git installed locally
- Your project ready for deployment

## Step 1: Upload Your Project

### Option A: Using Git (Recommended)
1. Push your project to GitHub/GitLab
2. In PythonAnywhere Bash console:
```bash
cd ~
git clone https://github.com/yourusername/Online_Judge.git
cd Online_Judge
```

### Option B: Upload Files
1. Use PythonAnywhere's file manager to upload your project
2. Extract to `/home/aasoj/Online_Judge/`

## Step 2: Configure Settings

1. Create `.env` file (optional):
```bash
cp .env.production .env
# Edit .env with your actual values
```

## Step 3: Run Deployment Script

```bash
cd ~/Online_Judge
python3.13 deploy_pythonanywhere.py
```

## Step 4: Configure Web App

1. Go to PythonAnywhere Dashboard → Web
2. Create new web app (Python 3.13, Manual configuration)
3. Set these configurations:

### WSGI Configuration
- **WSGI file**: `/home/aasoj/Online_Judge/wsgi_pythonanywhere.py`

### Static Files
- **URL**: `/static/`
- **Directory**: `/home/aasoj/Online_Judge/staticfiles/`

### Media Files (if needed)
- **URL**: `/media/`
- **Directory**: `/home/aasoj/Online_Judge/media/`

## Step 5: Create Admin User

```bash
cd ~/Online_Judge
python3.13 manage.py createsuperuser
```

## Step 6: Test Your Application

1. Visit `https://aasoj.pythonanywhere.com`
2. Test login/registration
3. Test problem submission (Note: Code execution may be limited on free accounts)

## Important Notes

### Code Execution Limitations
- **Free accounts**: Limited subprocess execution
- **Paid accounts**: Full subprocess support for code compilation/execution
- Consider using external judge APIs for free accounts

### Database Options
- **SQLite**: Works on free accounts (default)
- **MySQL**: Available on paid accounts (recommended for production)

### Static Files
- Collected automatically during deployment
- Served by PythonAnywhere's static file server

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Check Python version (use 3.13)
   - Verify all packages installed: `pip3.13 install --user -r requirements_pythonanywhere.txt`

2. **Static Files Not Loading**
   - Run: `python3.13 manage.py collectstatic`
   - Check static files configuration in web app settings

3. **Database Errors**
   - Run migrations: `python3.13 manage.py migrate`

4. **Code Execution Not Working**
   - Free accounts have subprocess limitations
   - Consider upgrading to paid account or using external judge services

### Logs
- Check error logs in PythonAnywhere dashboard
- Use `print()` statements for debugging

## Security Checklist

- [ ] `DEBUG = False` in production settings
- [ ] Strong `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` properly configured
- [ ] HTTPS settings enabled
- [ ] Email credentials secured

## Maintenance

### Updating Your App
```bash
cd ~/Online_Judge
git pull origin main
python3.13 manage.py migrate
python3.13 manage.py collectstatic --noinput
# Reload web app from dashboard
```

### Backup Database
```bash
cd ~/Online_Judge
python3.13 manage.py dumpdata > backup.json
```

## Support

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/
- Project Issues: Create GitHub issue

---

**Good luck with your deployment! 🚀**