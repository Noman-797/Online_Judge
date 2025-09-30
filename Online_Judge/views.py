from django.shortcuts import render
from problems.models import Problem, Category
from submissions.models import Submission
from django.contrib.auth.models import User


def home(request):
    recent_problems = Problem.objects.filter(is_active=True)[:6]
    total_problems = Problem.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    total_submissions = Submission.objects.count()
    
    context = {
        'recent_problems': recent_problems,
        'total_problems': total_problems,
        'total_users': total_users,
        'total_submissions': total_submissions,
    }
    return render(request, 'home.html', context)