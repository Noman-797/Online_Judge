from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils._os import safe_join
from django.conf import settings
from .models import Problem, Category, TestCase
from .forms import ProblemForm, TestCaseForm, CategoryForm
from submissions.models import Submission
import os
import re


@login_required
def problem_list(request):
    problems = Problem.objects.filter(is_active=True, contest_only=False).order_by('created_at')
    categories = Category.objects.all()
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        problems = problems.filter(category_id=category_id)
    
    # Filter by difficulty
    difficulty = request.GET.get('difficulty')
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    
    # Search
    search = request.GET.get('search')
    if search:
        problems = problems.filter(
            Q(title__icontains=search) | 
            Q(tags__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(problems, 20)
    page = request.GET.get('page')
    problems = paginator.get_page(page)
    
    # Get solved problems for the user (exclude test submissions)
    solved_problem_ids = set()
    if request.user.is_authenticated:
        solved_problem_ids = set(
            Submission.objects.filter(
                user=request.user,
                verdict='AC',
                is_test=False
            ).values_list('problem_id', flat=True)
        )
    
    context = {
        'problems': problems,
        'categories': categories,
        'current_category': category_id,
        'current_difficulty': difficulty,
        'search_query': search,
        'is_paginated': problems.has_other_pages,
        'page_obj': problems,
        'solved_problem_ids': solved_problem_ids,
    }
    return render(request, 'problems/problem_list.html', context)





@login_required
def problem_solve(request, slug):
    # Validate slug to prevent path traversal
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        messages.error(request, 'Invalid problem identifier.')
        return redirect('problems:problem_list')
    
    problem = get_object_or_404(Problem, slug=slug, is_active=True, contest_only=False)
    return render(request, 'problems/problem_solve.html', {'problem': problem})


def is_staff(user):
    return user.is_staff


@login_required
@user_passes_test(is_staff)
def admin_problems(request):
    problems = Problem.objects.all().order_by('created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        problems = problems.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # Filter by difficulty
    difficulty = request.GET.get('difficulty')
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'active':
        problems = problems.filter(is_active=True)
    elif status == 'inactive':
        problems = problems.filter(is_active=False)
    
    paginator = Paginator(problems, 20)
    page = request.GET.get('page')
    problems = paginator.get_page(page)
    
    return render(request, 'problems/admin_problems.html', {'problems': problems})


@login_required
@user_passes_test(is_staff)
def add_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.created_by = request.user
            problem.save()
            messages.success(request, 'Problem added successfully!')
            return redirect('problems:admin_problems')
    else:
        form = ProblemForm()
    
    return render(request, 'problems/add_problem.html', {'form': form})


@login_required
@user_passes_test(is_staff)
def edit_problem(request, slug):
    problem = get_object_or_404(Problem, slug=slug)
    
    if request.method == 'POST':
        form = ProblemForm(request.POST, instance=problem)
        if form.is_valid():
            form.save()
            messages.success(request, 'Problem updated successfully!')
            return redirect('problems:admin_problems')
    else:
        form = ProblemForm(instance=problem)
    
    return render(request, 'problems/edit_problem.html', {'form': form, 'problem': problem})


@login_required
@user_passes_test(is_staff)
def manage_test_cases(request, slug):
    problem = get_object_or_404(Problem, slug=slug)
    test_cases = TestCase.objects.filter(problem=problem).order_by('id')
    
    if request.method == 'POST':
        form = TestCaseForm(request.POST)
        if form.is_valid():
            test_case = form.save(commit=False)
            test_case.problem = problem
            test_case.save()
            messages.success(request, 'Test case added successfully!')
            return redirect('problems:manage_test_cases', slug=slug)
    else:
        form = TestCaseForm()
    
    return render(request, 'problems/manage_test_cases.html', {
        'problem': problem,
        'test_cases': test_cases,
        'form': form
    })


@login_required
@user_passes_test(is_staff)
def manage_categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'problems/manage_categories.html', {'categories': categories})


@login_required
@user_passes_test(is_staff)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('problems:manage_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'problems/add_category.html', {'form': form})


@login_required
@user_passes_test(is_staff)
def delete_problem(request, slug):
    problem = get_object_or_404(Problem, slug=slug)
    
    if request.method == 'POST':
        problem.delete()
        messages.success(request, f'Problem "{problem.title}" deleted successfully!')
        return redirect('problems:admin_problems')
    
    return render(request, 'problems/delete_problem.html', {'problem': problem})


@login_required
@user_passes_test(is_staff)
def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('problems:manage_categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'problems/edit_category.html', {'form': form, 'category': category})


@login_required
@user_passes_test(is_staff)
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    
    # Check if category has problems
    if category.problem_set.count() > 0:
        messages.error(request, f'Cannot delete category "{category.name}" because it has {category.problem_set.count()} problems.')
        return redirect('problems:manage_categories')
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('problems:manage_categories')
    
    return render(request, 'problems/delete_category.html', {'category': category})


@login_required
@user_passes_test(is_staff)
def edit_test_case(request, test_case_id):
    test_case = get_object_or_404(TestCase, id=test_case_id)
    problem = test_case.problem
    
    if request.method == 'POST':
        form = TestCaseForm(request.POST, instance=test_case)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test case updated successfully!')
            return redirect('problems:manage_test_cases', slug=problem.slug)
    else:
        form = TestCaseForm(instance=test_case)
    
    return render(request, 'problems/edit_test_case.html', {
        'form': form,
        'test_case': test_case,
        'problem': problem
    })


@login_required
@user_passes_test(is_staff)
def delete_test_case(request, test_case_id):
    test_case = get_object_or_404(TestCase, id=test_case_id)
    problem = test_case.problem
    
    if request.method == 'POST':
        test_case.delete()
        messages.success(request, 'Test case deleted successfully!')
        return redirect('problems:manage_test_cases', slug=problem.slug)
    
    return render(request, 'problems/delete_test_case.html', {
        'test_case': test_case,
        'problem': problem
    })