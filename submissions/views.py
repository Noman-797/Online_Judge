from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from problems.models import Problem
from .models import Submission
from .forms import SubmissionForm
from judge.evaluator import CodeEvaluator
from judge.queue_manager import submission_queue
import threading
import json


@login_required
def submit_solution(request, slug):
    problem = get_object_or_404(Problem, slug=slug, is_active=True, contest_only=False)
    
    if request.method == 'POST':
        # Handle AJAX submission
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            code = request.POST.get('code', '').strip()
            language = request.POST.get('language', 'cpp')
            
            if not code:
                return JsonResponse({
                    'verdict': 'CE',
                    'message': 'No code provided',
                    'execution_time': 0,
                    'memory_used': 0,
                    'test_cases_passed': 0,
                    'total_test_cases': 0
                })
            
            # Create submission first
            submission = Submission.objects.create(
                user=request.user,
                problem=problem,
                code=code,
                language=language
            )
            
            # Check if problem is contest-only (uses queue system)
            if problem.contest_only:
                # Use queue for contest-only problems
                submission_queue.add_submission(submission.id)
                return JsonResponse({
                    'verdict': 'QUEUED',
                    'message': 'Contest submission queued',
                    'submission_id': submission.id,
                    'queue_position': submission_queue.get_queue_position(submission.id),
                    'queue_size': submission_queue.get_queue_size(),
                    'execution_time': 0,
                    'memory_used': 0,
                    'test_cases_passed': 0,
                    'total_test_cases': 0
                })
            else:
                # Direct evaluation for regular submissions
                from judge.multi_language_evaluator import MultiLanguageEvaluator
                evaluator = MultiLanguageEvaluator()
                test_cases = problem.test_cases.all()
                
                result = evaluator.evaluate_submission(
                    code=code,
                    language=language,
                    test_cases=test_cases,
                    time_limit=problem.time_limit,
                    memory_limit=problem.memory_limit
                )
                
                # Update submission with results
                submission.verdict = result['verdict']
                submission.execution_time = result.get('execution_time')
                submission.memory_used = result.get('memory_used')
                submission.compilation_error = result.get('compilation_error', '')
                submission.runtime_error = result.get('runtime_error', '')
                submission.test_cases_passed = result.get('test_cases_passed', 0)
                submission.total_test_cases = result.get('total_test_cases', 0)
                submission.save()
                
                return JsonResponse({
                    'verdict': submission.verdict,
                    'message': 'Submission evaluated',
                    'submission_id': submission.id,
                    'execution_time': float(submission.execution_time) if submission.execution_time else 0,
                    'memory_used': submission.memory_used or 0,
                    'test_cases_passed': submission.test_cases_passed or 0,
                    'total_test_cases': submission.total_test_cases or 0
                })
        
        # Handle regular form submission
        code = request.POST.get('code', '').strip()
        language = request.POST.get('language', 'cpp')
        
        if not code:
            messages.error(request, 'Please provide your code before submitting.')
            return render(request, 'submissions/submit.html', {'problem': problem})
        
        # Create submission first
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language
        )
        
        # Check if problem is contest-only (uses queue system)
        if problem.contest_only:
            # Use queue for contest-only problems
            submission_queue.add_submission(submission.id)
            messages.success(request, 'Contest submission queued for evaluation!')
        else:
            # Direct evaluation for regular submissions
            from judge.multi_language_evaluator import MultiLanguageEvaluator
            evaluator = MultiLanguageEvaluator()
            test_cases = problem.test_cases.all()
            
            result = evaluator.evaluate_submission(
                code=code,
                language=language,
                test_cases=test_cases,
                time_limit=problem.time_limit,
                memory_limit=problem.memory_limit
            )
            
            # Update submission with results
            submission.verdict = result['verdict']
            submission.execution_time = result.get('execution_time')
            submission.memory_used = result.get('memory_used')
            submission.compilation_error = result.get('compilation_error', '')
            submission.runtime_error = result.get('runtime_error', '')
            submission.test_cases_passed = result.get('test_cases_passed', 0)
            submission.total_test_cases = result.get('total_test_cases', 0)
            submission.save()
            
            messages.success(request, 'Submission evaluated successfully!')
        
        # Redirect to submission detail page
        return redirect('submissions:submission_detail', submission_id=submission.id)
    
    # Get recent submissions for this problem
    recent_submissions = Submission.objects.filter(
        user=request.user, 
        problem=problem,
        is_test=False
    ).order_by('-submitted_at')[:5]
    
    return render(request, 'submissions/submit.html', {
        'problem': problem,
        'recent_submissions': recent_submissions
    })


@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    return render(request, 'submissions/detail.html', {'submission': submission})


@login_required
def my_submissions(request):
    submissions = Submission.objects.filter(user=request.user, is_test=False).order_by('-submitted_at')
    
    # Filter by verdict
    verdict = request.GET.get('verdict')
    if verdict:
        submissions = submissions.filter(verdict=verdict)
    
    # Filter by problem
    problem_id = request.GET.get('problem')
    if problem_id:
        submissions = submissions.filter(problem_id=problem_id)
    
    paginator = Paginator(submissions, 20)
    page = request.GET.get('page')
    submissions = paginator.get_page(page)
    
    return render(request, 'submissions/my_submissions.html', {
        'submissions': submissions,
        'current_verdict': verdict,
        'is_paginated': submissions.has_other_pages,
        'page_obj': submissions,
    })


@login_required
def all_submissions(request):
    submissions = Submission.objects.filter(is_test=False).order_by('-submitted_at')
    
    # Filter by verdict
    verdict = request.GET.get('verdict')
    if verdict:
        submissions = submissions.filter(verdict=verdict)
    
    paginator = Paginator(submissions, 20)
    page = request.GET.get('page')
    submissions = paginator.get_page(page)
    
    return render(request, 'submissions/all_submissions.html', {
        'submissions': submissions,
        'current_verdict': verdict,
        'is_paginated': submissions.has_other_pages,
        'page_obj': submissions,
    })


@login_required
def test_code(request, slug):
    """AJAX endpoint to test code against sample test cases only"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    problem = get_object_or_404(Problem, slug=slug, is_active=True, contest_only=False)
    
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        language = data.get('language', 'cpp')
        
        if not code:
            return JsonResponse({
                'verdict': 'CE',
                'execution_time': 0,
                'memory_used': 0,
                'test_cases_passed': 0,
                'total_test_cases': 0,
                'error_message': 'No code provided'
            })
        
        # Create temporary submission for testing (not saved to DB)
        temp_submission = Submission(
            user=request.user,
            problem=problem,
            code=code,
            language=language,
            is_test=True
        )
        
        # Evaluate against sample test cases only
        evaluator = CodeEvaluator(temp_submission)
        evaluator.evaluate(sample_only=True)
        
        return JsonResponse({
            'verdict': temp_submission.verdict,
            'execution_time': temp_submission.execution_time or 0,
            'memory_used': temp_submission.memory_used or 0,
            'test_cases_passed': temp_submission.test_cases_passed or 0,
            'total_test_cases': temp_submission.total_test_cases or 0,
            'error_message': temp_submission.compilation_error or temp_submission.runtime_error or None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({
            'verdict': 'RE',
            'execution_time': 0,
            'memory_used': 0,
            'test_cases_passed': 0,
            'total_test_cases': 0,
            'error_message': str(e)
        }, status=500)


@login_required
def submit_ajax(request, slug):
    """AJAX endpoint to submit code for full evaluation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    problem = get_object_or_404(Problem, slug=slug, is_active=True, contest_only=False)
    
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        language = data.get('language', 'cpp')
        
        if not code:
            return JsonResponse({
                'verdict': 'CE',
                'error_message': 'No code provided'
            })
        
        # Create submission first
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language
        )
        
        # Check if problem is contest-only (uses queue system)
        if problem.contest_only:
            # Use queue for contest-only problems
            submission_queue.add_submission(submission.id)
            return JsonResponse({
                'verdict': 'QUEUED',
                'submission_id': submission.id,
                'queue_position': submission_queue.get_queue_position(submission.id),
                'queue_size': submission_queue.get_queue_size(),
                'execution_time': 0,
                'memory_used': 0,
                'test_cases_passed': 0,
                'total_test_cases': 0,
                'error_message': None
            })
        else:
            # Direct evaluation for regular submissions
            from judge.multi_language_evaluator import MultiLanguageEvaluator
            evaluator = MultiLanguageEvaluator()
            test_cases = problem.test_cases.all()
            
            result = evaluator.evaluate_submission(
                code=code,
                language=language,
                test_cases=test_cases,
                time_limit=problem.time_limit,
                memory_limit=problem.memory_limit
            )
            
            # Update submission with results
            submission.verdict = result['verdict']
            submission.execution_time = result.get('execution_time')
            submission.memory_used = result.get('memory_used')
            submission.compilation_error = result.get('compilation_error', '')
            submission.runtime_error = result.get('runtime_error', '')
            submission.test_cases_passed = result.get('test_cases_passed', 0)
            submission.total_test_cases = result.get('total_test_cases', 0)
            submission.save()
            
            return JsonResponse({
                'verdict': submission.verdict,
                'submission_id': submission.id,
                'execution_time': float(submission.execution_time) if submission.execution_time else 0,
                'memory_used': submission.memory_used or 0,
                'test_cases_passed': submission.test_cases_passed or 0,
                'total_test_cases': submission.total_test_cases or 0,
                'error_message': submission.compilation_error or submission.runtime_error or None
            })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def check_submission_status(request, submission_id):
    """AJAX endpoint to check submission status"""
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    
    response_data = {
        'verdict': submission.verdict,
        'verdict_display': submission.get_verdict_display(),
        'problem_title': submission.problem.title,
        'execution_time': submission.execution_time,
        'memory_used': submission.memory_used,
        'test_cases_passed': submission.test_cases_passed,
        'total_test_cases': submission.total_test_cases,
    }
    
    # Add queue info if still queued
    if submission.verdict == 'QUEUED':
        response_data['queue_position'] = submission_queue.get_queue_position(submission.id)
        response_data['queue_size'] = submission_queue.get_queue_size()
    
    return JsonResponse(response_data)


@login_required
def queue_status(request):
    """AJAX endpoint to get current queue status"""
    return JsonResponse({
        'queue_size': submission_queue.get_queue_size(),
        'active_workers': submission_queue.active_workers,
        'max_workers': submission_queue.max_workers
    })


@login_required
def recent_submissions(request):
    """AJAX endpoint to get user's recent submissions"""
    since_timestamp = request.GET.get('since', 0)
    contest_slug = request.GET.get('contest')
    
    try:
        since_time = timezone.datetime.fromtimestamp(int(since_timestamp) / 1000, tz=timezone.utc)
    except (ValueError, TypeError):
        since_time = timezone.now() - timezone.timedelta(minutes=5)
    
    submissions_query = Submission.objects.filter(
        user=request.user,
        submitted_at__gte=since_time,
        is_test=False
    ).order_by('-submitted_at')
    
    # Filter by contest if provided
    if contest_slug:
        from contests.models import Contest, ContestProblem
        try:
            contest = Contest.objects.get(slug=contest_slug, is_active=True)
            contest_problem_ids = ContestProblem.objects.filter(contest=contest).values_list('problem_id', flat=True)
            submissions_query = submissions_query.filter(problem_id__in=contest_problem_ids)
        except Contest.DoesNotExist:
            pass
    
    submissions = list(submissions_query.values(
        'id', 'verdict', 'submitted_at', 'problem__title'
    ))
    
    return JsonResponse({
        'submissions': submissions
    })