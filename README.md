# All About Semicolons - Online Judge System

A comprehensive online judge platform designed for students and beginners to practice C and C++ programming problems. Built with Django and styled with Tailwind CSS + DaisyUI.

## Features

### 🎯 Core Functionality
- **User Management**: Registration, login, logout, and user profiles
- **Problem Management**: Create, edit, and categorize programming problems
- **Code Submission**: Submit C/C++ solutions with real-time evaluation
- **Automated Judging**: Compile, run, and evaluate code against test cases
- **Admin Panel**: Comprehensive admin interface for managing problems and users

### 🔧 Technical Features
- **Sandboxed Execution**: Safe code execution with time and memory limits
- **Multiple Verdicts**: AC, WA, CE, RE, TLE, MLE, PE support
- **Real-time Updates**: AJAX-powered submission status updates
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS
- **SQLite Database**: Lightweight database for easy deployment

### 📊 User Features
- **Progress Tracking**: Track solved problems and submission history
- **Submission History**: View detailed submission results and code
- **Problem Filtering**: Filter by difficulty, category, and tags
- **Success Rate**: Calculate and display user success statistics

## Installation & Setup

### Prerequisites
- Python 3.8+
- GCC/G++ compiler (for code evaluation)
- Git (for version control)

### Local Development Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Online_Judge
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create sample data**
```bash
python create_sample_data.py
```

6. **Run development server**
```bash
python manage.py runserver
```

7. **Create admin user**
```bash
python manage.py create_admin
```

8. **Access the application**
- Open http://127.0.0.1:8000 in your browser
- Admin login: `ojadmin/OJAdmin2024!`
- Student login: `student/student123`
- Or register as a new user

## Project Structure

```
Online_Judge/
├── Online_Judge/          # Main project settings
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── accounts/              # User management app
│   ├── models.py         # User profile models
│   ├── views.py          # Authentication views
│   ├── forms.py          # User forms
│   └── management/       # Custom management commands
├── problems/              # Problem management app
│   ├── models.py         # Problem and category models
│   ├── views.py          # Problem CRUD views
│   ├── forms.py          # Problem forms
│   └── admin.py          # Admin interface
├── submissions/           # Code submission app
│   ├── models.py         # Submission models
│   ├── views.py          # Submission handling
│   └── forms.py          # Submission forms
├── judge/                 # Code evaluation engine
│   ├── evaluator.py      # Core evaluation logic
│   ├── compiler_check.py # Compiler verification
│   └── management/       # Testing commands
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── home.html         # Homepage
│   ├── accounts/         # User templates
│   ├── problems/         # Problem templates
│   ├── submissions/      # Submission templates
│   └── components/       # Reusable components
├── static/                # Static files
│   ├── css/              # Stylesheets
│   │   ├── custom.css    # Main stylesheet
│   │   └── responsive.css # Responsive styles
│   └── js/               # JavaScript files
├── temp/                  # Temporary files for code execution
├── db.sqlite3            # SQLite database
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── create_sample_data.py # Sample data creation script
├── setup_compiler.py     # Compiler setup utility
└── .env.example          # Environment variables template
```

## Usage Guide

### For Students/Users

1. **Register an Account**
   - Click "Register" and fill in your details
   - Verify your email and login

2. **Browse Problems**
   - Visit the Problems page
   - Filter by difficulty, category, or search by keywords
   - Click on any problem to view details

3. **Submit Solutions**
   - Click "Submit Solution" on any problem
   - Choose your language (C or C++)
   - Write your code in the editor
   - Submit and wait for evaluation results

4. **Track Progress**
   - Visit your Profile to see statistics
   - Check "My Submissions" for submission history
   - View detailed results for each submission

### For Administrators

1. **Access Admin Panel**
   - Login as staff user
   - Navigate to "Admin Panel" in the user menu

2. **Manage Problems**
   - Add new problems with descriptions and test cases
   - Edit existing problems
   - Manage test cases (sample and hidden)

3. **Monitor System**
   - View all submissions
   - Monitor user activity
   - Manage user accounts through Django admin

## Sample Problems Included

The system comes with 6 sample problems:

1. **Hello World** (Easy) - Basic output
2. **Sum of Two Numbers** (Easy) - Basic arithmetic
3. **Maximum of Array** (Easy) - Array processing
4. **Reverse String** (Easy) - String manipulation
5. **Factorial** (Medium) - Mathematical computation
6. **Bubble Sort** (Medium) - Sorting algorithm

## Code Evaluation System

### Supported Languages
- C (GCC compiler)
- C++ (G++ compiler with C++17 standard)

### Evaluation Process
1. **Compilation**: Code is compiled with appropriate compiler
2. **Execution**: Compiled program runs against test cases
3. **Verdict Assignment**: Based on execution results
4. **Resource Monitoring**: Time and memory usage tracking

### Possible Verdicts
- **AC (Accepted)**: Solution is correct
- **WA (Wrong Answer)**: Output doesn't match expected
- **CE (Compilation Error)**: Code failed to compile
- **RE (Runtime Error)**: Program crashed during execution
- **TLE (Time Limit Exceeded)**: Execution took too long
- **MLE (Memory Limit Exceeded)**: Used too much memory
- **PE (Presentation Error)**: Output format issues



## Security Considerations

### Code Execution Safety
- Sandboxed execution environment
- Time and memory limits enforced
- Temporary file cleanup
- Input validation and sanitization

### User Security
- CSRF protection enabled
- SQL injection prevention
- XSS protection
- Secure password hashing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Local Development Issues

**Compilation Errors**
- Ensure GCC/G++ is installed and in PATH
- Check compiler version compatibility

**Database Issues**
- Run `python manage.py migrate`
- Check SQLite file permissions

**Static Files Not Loading**
- Run `python manage.py collectstatic`
- Check STATIC_ROOT configuration



## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing GitHub issues
3. Create a new issue with detailed description

## Acknowledgments

- Django framework for the backend
- Tailwind CSS and DaisyUI for styling
- Font Awesome for icons
- SQLite for the database

---

**Happy Coding! 🚀**