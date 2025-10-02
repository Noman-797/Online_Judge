from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
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
            
            # Check if manual queue is enabled for contest problems
            from django.conf import settings
            if getattr(settings, 'ENABLE_MANUAL_QUEUE', False) and problem.contest_only:
                # Queue contest submissions for manual processing
                return JsonResponse({
                    'verdict': 'QUEUED',
                    'message': 'Contest submission queued for manual processing',
                    'submission_id': submission.id,
                    'execution_time': 0,
                    'memory_used': 0,
                    'test_cases_passed': 0,
                    'total_test_cases': 0
                })
            else:
                # Direct evaluation for regular problems
                evaluator = CodeEvaluator(submission)
                evaluator.evaluate()
                
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
        
        # Check if manual queue is enabled for contest problems
        from django.conf import settings
        if getattr(settings, 'ENABLE_MANUAL_QUEUE', False) and problem.contest_only:
            # Queue contest submissions for manual processing
            messages.success(request, 'Contest submission queued for manual processing!')
        else:
            # Direct evaluation for regular problems
            evaluator = CodeEvaluator(submission)
            evaluator.evaluate()
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
        
        # Check if manual queue is enabled for contest problems
        from django.conf import settings
        if getattr(settings, 'ENABLE_MANUAL_QUEUE', False) and problem.contest_only:
            # Queue contest submissions for manual processing
            return JsonResponse({
                'verdict': 'QUEUED',
                'submission_id': submission.id,
                'execution_time': 0,
                'memory_used': 0,
                'test_cases_passed': 0,
                'total_test_cases': 0,
                'error_message': None
            })
        else:
            # Direct evaluation for regular problems
            evaluator = CodeEvaluator(submission)
            evaluator.evaluate()
            
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
    
    return JsonResponse({
        'verdict': submission.verdict,
        'verdict_display': submission.get_verdict_display(),
        'problem_title': submission.problem.title,
        'execution_time': submission.execution_time,
        'memory_used': submission.memory_used,
        'test_cases_passed': submission.test_cases_passed,
        'total_test_cases': submission.total_test_cases,
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


@staff_member_required
def process_queue_manual(request):
    """Manual queue processing for PythonAnywhere"""
    if request.method == 'POST':
        limit = int(request.POST.get('limit', 5))
        queued_submissions = Submission.get_queued_submissions(limit=limit)
        
        results = []
        processed = 0
        failed = 0
        
        for submission in queued_submissions:
            try:
                from judge.evaluator import CodeEvaluator
                evaluator = CodeEvaluator(submission)
                evaluator.evaluate()
                success = submission.verdict != 'RE'
                
                results.append({
                    'id': submission.id,
                    'user': submission.user.username,
                    'problem': submission.problem.title,
                    'verdict': submission.verdict,
                    'success': success
                })
                
                if success:
                    processed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                failed += 1
                results.append({
                    'id': submission.id,
                    'user': submission.user.username,
                    'problem': submission.problem.title,
                    'verdict': 'ERROR',
                    'success': False,
                    'error': str(e)
                })
        
        return JsonResponse({
            'processed': processed,
            'failed': failed,
            'results': results
        })
    
    # GET request - show current queue status
    queued_count = Submission.objects.filter(verdict='QUEUED').count()
    recent_queued = Submission.objects.filter(verdict='QUEUED').order_by('submitted_at')[:10]
    
    return render(request, 'submissions/process_queue.html', {
        'queued_count': queued_count,
        'recent_queued': recent_queued,
    })


@staff_member_required
def queue_status_api(request):
    """API endpoint for queue status"""
    return JsonResponse({
        'queued': Submission.objects.filter(verdict='QUEUED').count(),
        'judging': Submission.objects.filter(verdict='JUDGING').count(),
        'recent_ac': Submission.objects.filter(verdict='AC').count(),
    })


@login_required
def check_pending_submissions(request):
    """AJAX endpoint to check for pending submissions and notify when completed"""
    user_submissions = Submission.objects.filter(
        user=request.user,
        verdict__in=['QUEUED', 'JUDGING'],
        is_test=False
    ).values('id', 'verdict', 'problem__title', 'submitted_at')
    
    # Check for recently completed submissions (last 60 seconds)
    recent_completed = Submission.objects.filter(
        user=request.user,
        judged_at__gte=timezone.now() - timezone.timedelta(seconds=60),
        verdict__in=['AC', 'WA', 'CE', 'RE', 'TLE', 'MLE', 'PE'],
        is_test=False
    ).values('id', 'verdict', 'problem__title', 'judged_at')
    
    return JsonResponse({
        'pending': list(user_submissions),
        'completed': list(recent_completed),
        'timestamp': timezone.now().isoformat()
    })