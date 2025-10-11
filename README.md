# All About Semicolons - Online Judge System

A comprehensive online judge platform designed for C/C++/Python programming practice and contests. Optimized for PythonAnywhere deployment.

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone <your-repo-url>
cd Online_Judge

# Create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies and setup
python setup.py

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### PythonAnywhere Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🎯 Features

### Core Functionality
- **Multi-language Support**: C, C++, and Python
- **Real-time Evaluation**: Automated code compilation and testing
- **Contest System**: Timed programming contests with leaderboards
- **User Management**: Registration, profiles, and progress tracking
- **Admin Panel**: Complete problem and user management
- **Communication System**: User-admin messaging

### Technical Features
- **Secure Execution**: Sandboxed code execution with time/memory limits
- **Multiple Verdicts**: AC, WA, CE, RE, TLE, MLE, PE support
- **Real-time Notifications**: AJAX-powered status updates
- **Responsive Design**: Mobile-friendly interface
- **Database Optimization**: Indexed queries for performance

## 📊 System Architecture

### Applications
- `accounts/` - User authentication and profiles
- `problems/` - Problem management and categories
- `submissions/` - Code submission and evaluation
- `judge/` - Core evaluation engine
- `contests/` - Contest management
- `communications/` - Messaging system

### Key Components
- **CodeEvaluator**: Handles compilation and execution
- **Queue System**: Manual processing for contest submissions
- **Notification System**: Real-time updates via JavaScript
- **Security Layer**: Input validation and sandboxing

## 🔧 Configuration

### Environment Variables (.env)
```bash
SECRET_KEY=your-secret-key
DEBUG=False
DB_NAME=yourusername$default
DB_USER=yourusername
DB_PASSWORD=your-password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
```

### Judge Settings
- Time Limit: 2 seconds
- Memory Limit: 128 MB
- Code Size Limit: 50 KB
- Compilation Timeout: 10 seconds

## 🛠️ Management Commands

```bash
# Create sample data
python manage.py create_sample_data

# Process queued submissions
python manage.py process_queued

# Create admin user
python manage.py create_admin
```

## 📱 API Endpoints

### Submissions
- `POST /submissions/ajax/<slug>/` - Submit code
- `GET /submissions/status/<id>/` - Check submission status
- `POST /submissions/test/<slug>/` - Test against samples

### Communications
- `GET /communications/check-unread/` - Check unread messages
- `POST /communications/send/` - Send message to admin

## 🔒 Security Features

- CSRF protection enabled
- SQL injection prevention
- XSS protection
- Input validation and sanitization
- Sandboxed code execution
- File size limitations
- Time and memory constraints

## 🎨 Frontend Technologies

- **Tailwind CSS + DaisyUI** - Modern UI framework
- **Font Awesome** - Icons
- **JavaScript** - Real-time features
- **AJAX** - Asynchronous operations

## 📈 Performance Optimizations

- Database indexing on frequently queried fields
- Pagination for large datasets
- Efficient submission queue processing
- Optimized compiler flags
- Static file compression

## 🐛 Troubleshooting

### Common Issues
1. **Compilation Errors**: Ensure GCC/G++ are installed
2. **Database Errors**: Check database credentials
3. **Static Files**: Run `collectstatic` command
4. **Permissions**: Check file/directory permissions

### Logs
- Django logs: Check console output
- PythonAnywhere: Web app error logs
- Database: MySQL slow query log

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Django framework
- Tailwind CSS and DaisyUI
- PythonAnywhere hosting
- Font Awesome icons

---

**Happy Coding! 🚀**

For support, visit: [All About Semicolons](https://allaboutsemicolons.site)