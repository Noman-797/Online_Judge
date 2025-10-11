from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils._os import safe_join
from django.conf import settings
from django.http import JsonResponse
from .models import Contest, ContestParticipation, ContestProblem, ContestAnnouncement
from .forms import ContestForm, ContestProblemForm, ContestAnnouncementForm
from submissions.models import Submission
import os
import re


def contest_list(request):
    contests = Contest.objects.filter(is_active=True).order_by('-start_time')
    
    # Separate by status
    upcoming = contests.filter(start_time__gt=timezone.now())
    running = contests.filter(start_time__lte=timezone.now(), end_time__gte=timezone.now())
    ended = contests.filter(end_time__lt=timezone.now())
    
    # Add pagination for ended contests (usually the most)
    paginator = Paginator(ended, 20)
    page = request.GET.get('page')
    ended_paginated = paginator.get_page(page)
    
    return render(request, 'contests/contest_list.html', {
        'upcoming': upcoming,
        'running': running,
        'ended': ended_paginated
    })


def contest_detail(request, slug):
    # Validate slug to prevent path traversal
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        messages.error(request, 'Invalid contest identifier.')
        return redirect('contests:contest_list')
    
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    contest_problems = ContestProblem.objects.filter(contest=contest).select_related('problem')
    
    participation = None
    is_banned = False
    is_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    
    if request.user.is_authenticated and not is_admin:
        participation = ContestParticipation.objects.filter(contest=contest, user=request.user).first()
        
        # Check if user is banned
        if participation and participation.is_banned:
            is_banned = True
        elif participation and contest.status == 'running' and not is_banned:
            return redirect('contests:contest_problems', slug=slug)
        
        # For past contests, allow direct access to problems
        if contest.status == 'ended':
            participation = True
    
    return render(request, 'contests/contest_detail.html', {
        'contest': contest,
        'contest_problems': contest_problems,
        'participation': participation,
        'is_banned': is_banned,
        'is_admin': is_admin
    })


@login_required
def contest_problems(request, slug):
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    contest_problems = ContestProblem.objects.filter(contest=contest).select_related('problem')
    
    # Check if user is participating
    participation = None
    is_admin = request.user.is_staff or request.user.is_superuser
    
    if request.user.is_authenticated and not is_admin:
        participation = ContestParticipation.objects.filter(contest=contest, user=request.user).first()
        
        # Check if user is banned
        if participation and participation.is_banned:
            messages.error(request, 'You have been banned from this contest.')
            return redirect('contests:contest_detail', slug=slug)
    
    # For past contests or admin users, allow access without participation
    if contest.status == 'ended' or is_admin:
        participation = True  # Allow access to past contests and admin users
    
    # Get solved problems for the user (exclude test submissions)
    solved_problem_ids = set()
    if request.user.is_authenticated:
        solved_problem_ids = set(
            Submission.objects.filter(
                user=request.user,
                problem__in=[cp.problem for cp in contest_problems],
                verdict='AC',
                is_test=False
            ).values_list('problem_id', flat=True)
        )
    
    return render(request, 'contests/contest_problems.html', {
        'contest': contest,
        'contest_problems': contest_problems,
        'participation': participation,
        'solved_problem_ids': solved_problem_ids,
        'is_admin': is_admin
    })


@login_required
def join_contest(request, slug):
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    
    # Prevent admin users from joining contests
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, 'Admin users cannot participate in contests.')
        return redirect('contests:contest_detail', slug=slug)
    
    if contest.status == 'ended':
        messages.error(request, 'Contest has already ended.')
        return redirect('contests:contest_detail', slug=slug)
    
    participation, created = ContestParticipation.objects.get_or_create(
        contest=contest, user=request.user
    )
    
    if created:
        if contest.status == 'upcoming':
            messages.success(request, 'Successfully registered! You can enter when contest starts.')
            return redirect('contests:contest_detail', slug=slug)
        else:
            messages.success(request, 'Successfully registered for the contest!')
            return redirect('contests:contest_problems', slug=slug)
    else:
        messages.info(request, 'You are already registered for this contest.')
        if contest.status == 'running':
            return redirect('contests:contest_problems', slug=slug)
        else:
            return redirect('contests:contest_detail', slug=slug)


def contest_leaderboard(request, slug):
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    
    # Get contest problems with optimization
    contest_problems = ContestProblem.objects.filter(contest=contest).select_related('problem')
    contest_problem_ids = [cp.problem.id for cp in contest_problems]
    
    # Get all participations with user data, excluding admin users
    participations = ContestParticipation.objects.filter(
        contest=contest,
        user__is_staff=False,
        user__is_superuser=False
    ).select_related('user')
    
    # Bulk fetch all submissions for the contest period (exclude test submissions)
    all_submissions = Submission.objects.filter(
        problem_id__in=contest_problem_ids,
        submitted_at__gte=contest.start_time,
        submitted_at__lte=contest.end_time,
        user__in=[p.user for p in participations],
        is_test=False
    ).select_related('user', 'problem').order_by('user_id', 'problem_id', 'submitted_at')
    
    # Group submissions by user and problem
    user_submissions = {}
    for submission in all_submissions:
        user_id = submission.user_id
        problem_id = submission.problem_id
        if user_id not in user_submissions:
            user_submissions[user_id] = {}
        if problem_id not in user_submissions[user_id]:
            user_submissions[user_id][problem_id] = []
        user_submissions[user_id][problem_id].append(submission)
    
    # Calculate scores for each participant
    leaderboard_data = []
    for participation in participations:
        problems_solved = 0
        total_penalty = 0
        user_id = participation.user_id
        
        if user_id in user_submissions:
            for problem_id in contest_problem_ids:
                if problem_id in user_submissions[user_id]:
                    submissions = user_submissions[user_id][problem_id]
                    
                    # Find AC submission
                    ac_submission = next((s for s in submissions if s.verdict == 'AC'), None)
                    if ac_submission:
                        problems_solved += 1
                        
                        # Calculate penalty time
                        wrong_attempts = sum(1 for s in submissions 
                                           if s.submitted_at < ac_submission.submitted_at 
                                           and s.verdict in ['WA', 'RE', 'TLE', 'MLE', 'PE'])
                        
                        submission_time_minutes = int((ac_submission.submitted_at - contest.start_time).total_seconds() / 60)
                        penalty_time = submission_time_minutes + (wrong_attempts * 10)
                        total_penalty += penalty_time
        
        leaderboard_data.append({
            'user': participation.user,
            'problems_solved': problems_solved,
            'total_penalty': total_penalty,
            'start_time': participation.start_time
        })
    
    # Sort by ACM ICPC rules
    leaderboard_data.sort(key=lambda x: (-x['problems_solved'], x['total_penalty']))
    
    # Add pagination
    paginator = Paginator(leaderboard_data, 20)  # 20 participants per page
    page = request.GET.get('page')
    participations = paginator.get_page(page)
    
    return render(request, 'contests/leaderboard.html', {
        'contest': contest,
        'participations': participations
    })


def is_staff(user):
    return user.is_staff


@login_required
@user_passes_test(is_staff)
def admin_contests(request):
    contests = Contest.objects.all().order_by('-start_time')
    
    # Separate by status
    upcoming = contests.filter(start_time__gt=timezone.now())
    running = contests.filter(start_time__lte=timezone.now(), end_time__gte=timezone.now())
    ended = contests.filter(end_time__lt=timezone.now())
    
    return render(request, 'contests/admin_contests.html', {
        'upcoming': upcoming,
        'running': running,
        'ended': ended
    })


@login_required
@user_passes_test(is_staff)
def add_contest(request):
    if request.method == 'POST':
        form = ContestForm(request.POST)
        if form.is_valid():
            contest = form.save(commit=False)
            contest.created_by = request.user
            contest.save()
            messages.success(request, 'Contest created successfully!')
            return redirect('contests:admin_contests')
    else:
        form = ContestForm()
    
    return render(request, 'contests/add_contest.html', {'form': form})


@login_required
@user_passes_test(is_staff)
def manage_contest_problems(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    contest_problems = ContestProblem.objects.filter(contest=contest).order_by('order')
    
    if request.method == 'POST':
        form = ContestProblemForm(request.POST)
        if form.is_valid():
            contest_problem = form.save(commit=False)
            contest_problem.contest = contest
            contest_problem.save()
            messages.success(request, 'Problem added to contest!')
            return redirect('contests:manage_problems', slug=slug)
    else:
        # Set initial values
        next_order = contest_problems.count() + 1
        form = ContestProblemForm(initial={'order': next_order, 'points': 1})
    
    return render(request, 'contests/manage_contest_problems.html', {
        'contest': contest,
        'contest_problems': contest_problems,
        'form': form
    })


@login_required
@user_passes_test(is_staff)
def remove_contest_problem(request, slug, problem_id):
    contest = get_object_or_404(Contest, slug=slug)
    contest_problem = get_object_or_404(ContestProblem, id=problem_id, contest=contest)
    contest_problem.delete()
    
    messages.success(request, 'Problem removed from contest!')
    return redirect('contests:manage_problems', slug=slug)


@login_required
@user_passes_test(is_staff)
def edit_contest_problem(request, slug, problem_id):
    contest = get_object_or_404(Contest, slug=slug)
    contest_problem = get_object_or_404(ContestProblem, id=problem_id, contest=contest)
    
    if request.method == 'POST':
        form = ContestProblemForm(request.POST, instance=contest_problem)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contest problem updated!')
            return redirect('contests:manage_problems', slug=slug)
    else:
        form = ContestProblemForm(instance=contest_problem)
    
    return render(request, 'contests/edit_contest_problem.html', {
        'contest': contest,
        'contest_problem': contest_problem,
        'form': form
    })


@login_required
@user_passes_test(is_staff)
def edit_contest(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    
    # Allow editing upcoming and running contests
    if contest.status == 'ended':
        messages.error(request, 'Ended contests cannot be edited.')
        return redirect('contests:admin_contests')
    
    if request.method == 'POST':
        form = ContestForm(request.POST, instance=contest)
        if form.is_valid():
            old_slug = contest.slug
            contest = form.save()
            # If slug changed, show warning about URL change
            if old_slug != contest.slug:
                messages.warning(request, f'Contest URL changed from /{old_slug}/ to /{contest.slug}/')
            messages.success(request, 'Contest updated successfully!')
            return redirect('contests:admin_contests')
    else:
        form = ContestForm(instance=contest)
    
    return render(request, 'contests/edit_contest.html', {
        'form': form,
        'contest': contest
    })


@login_required
@user_passes_test(is_staff)
def delete_contest(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    contest_title = contest.title
    contest.delete()
    messages.success(request, f'Contest "{contest_title}" deleted successfully!')
    return redirect('contests:admin_contests')


@login_required
@user_passes_test(is_staff)
def monitor_contest(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    participations = ContestParticipation.objects.filter(contest=contest).select_related('user')
    
    contest_problem_ids = ContestProblem.objects.filter(contest=contest).values_list('problem_id', flat=True)
    recent_submissions = Submission.objects.filter(
        problem_id__in=contest_problem_ids,
        submitted_at__gte=contest.start_time,
        submitted_at__lte=contest.end_time,
        is_test=False
    ).select_related('user', 'problem').order_by('-submitted_at')[:50]
    
    return render(request, 'contests/monitor_contest.html', {
        'contest': contest,
        'participations': participations,
        'recent_submissions': recent_submissions
    })


@login_required
@user_passes_test(is_staff)
def view_submission_code(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Get contest from referrer or session to validate submission belongs to current contest
    contest_slug = request.GET.get('contest')
    if contest_slug:
        contest = get_object_or_404(Contest, slug=contest_slug)
        contest_problem_ids = ContestProblem.objects.filter(contest=contest).values_list('problem_id', flat=True)
        
        # Ensure submission belongs to this contest
        if submission.problem_id not in contest_problem_ids:
            messages.error(request, 'Submission does not belong to this contest.')
            return redirect('contests:monitor_contest', slug=contest_slug)
    
    return render(request, 'contests/view_code.html', {
        'submission': submission
    })


@login_required
@user_passes_test(is_staff)
def ban_participant(request, slug, user_id):
    contest = get_object_or_404(Contest, slug=slug)
    participation = get_object_or_404(ContestParticipation, contest=contest, user_id=user_id)
    participation.is_banned = True
    participation.save()
    messages.success(request, f'User {participation.user.username} banned from contest!')
    return redirect('contests:monitor_contest', slug=slug)


@login_required
@user_passes_test(is_staff)
def unban_participant(request, slug, user_id):
    contest = get_object_or_404(Contest, slug=slug)
    participation = get_object_or_404(ContestParticipation, contest=contest, user_id=user_id)
    participation.is_banned = False
    participation.save()
    messages.success(request, f'User {participation.user.username} unbanned from contest!')
    return redirect('contests:monitor_contest', slug=slug)


@login_required
@user_passes_test(is_staff)
def user_submissions(request, slug, user_id):
    contest = get_object_or_404(Contest, slug=slug)
    user = get_object_or_404(User, id=user_id)
    
    contest_problem_ids = ContestProblem.objects.filter(contest=contest).values_list('problem_id', flat=True)
    submissions = Submission.objects.filter(
        user=user,
        problem_id__in=contest_problem_ids,
        submitted_at__gte=contest.start_time,
        submitted_at__lte=contest.end_time,
        is_test=False
    ).select_related('problem').order_by('-submitted_at')
    
    return render(request, 'contests/user_submissions.html', {
        'contest': contest,
        'user': user,
        'submissions': submissions
    })


@login_required
def contest_problem_solve(request, slug, problem_slug):
    """Contest-specific problem solve page"""
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    contest_problem = get_object_or_404(ContestProblem.objects.select_related('problem').prefetch_related('problem__test_cases'), contest=contest, problem__slug=problem_slug)
    problem = contest_problem.problem
    
    # Check if user can access this contest problem
    participation = None
    is_admin = request.user.is_staff or request.user.is_superuser
    
    if request.user.is_authenticated and not is_admin:
        participation = ContestParticipation.objects.filter(contest=contest, user=request.user).first()
        
        # Check if user is banned
        if participation and participation.is_banned:
            messages.error(request, 'You have been banned from this contest.')
            return redirect('contests:contest_detail', slug=slug)
    
    # For past contests or admin users, allow access without participation
    if contest.status == 'ended' or is_admin:
        participation = True
    elif contest.status == 'running' and not participation:
        messages.error(request, 'You must join the contest first.')
        return redirect('contests:contest_detail', slug=slug)
    
    # Get user's latest submission for this problem
    latest_submission = None
    if request.user.is_authenticated:
        latest_submission = Submission.objects.filter(
            user=request.user,
            problem=problem,
            is_test=False
        ).order_by('-submitted_at').first()
    
    # Get next and previous problems in contest
    next_problem = ContestProblem.objects.filter(
        contest=contest,
        order__gt=contest_problem.order
    ).order_by('order').first()
    
    prev_problem = ContestProblem.objects.filter(
        contest=contest,
        order__lt=contest_problem.order
    ).order_by('-order').first()
    
    return render(request, 'contests/contest_problem_solve.html', {
        'contest': contest,
        'contest_problem': contest_problem,
        'problem': problem,
        'latest_submission': latest_submission,
        'next_problem': next_problem,
        'prev_problem': prev_problem,
        'current_order': contest_problem.order,
        'is_admin': is_admin
    })


@login_required
def contest_test_code(request, slug, problem_slug):
    """AJAX endpoint to test code against sample test cases for contest problems"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    contest_problem = get_object_or_404(ContestProblem, contest=contest, problem__slug=problem_slug)
    problem = contest_problem.problem
    
    # Check access
    is_admin = request.user.is_staff or request.user.is_superuser
    
    if not is_admin:
        participation = ContestParticipation.objects.filter(contest=contest, user=request.user).first()
        if contest.status == 'running' and not participation:
            return JsonResponse({'error': 'Must join contest first'}, status=403)
        if participation and participation.is_banned:
            return JsonResponse({'error': 'Banned from contest'}, status=403)
    elif contest.status == 'running':
        return JsonResponse({'error': 'Admin users cannot test code during live contests'}, status=403)
    
    try:
        import json
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
        
        # Create temporary submission for testing
        temp_submission = Submission(
            user=request.user,
            problem=problem,
            code=code,
            language=language,
            is_test=True
        )
        
        # Evaluate against sample test cases only
        try:
            from judge.evaluator import CodeEvaluator
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
        except Exception as e:
            return JsonResponse({
                'verdict': 'RE',
                'execution_time': 0,
                'memory_used': 0,
                'test_cases_passed': 0,
                'total_test_cases': 0,
                'error_message': f'Test evaluation failed: {str(e)[:100]}'
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
def contest_submit_ajax(request, slug, problem_slug):
    """AJAX endpoint to submit code for contest problems"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    contest_problem = get_object_or_404(ContestProblem, contest=contest, problem__slug=problem_slug)
    problem = contest_problem.problem
    
    # Check access
    is_admin = request.user.is_staff or request.user.is_superuser
    
    if not is_admin:
        participation = ContestParticipation.objects.filter(contest=contest, user=request.user).first()
        if contest.status == 'running' and not participation:
            return JsonResponse({'error': 'Must join contest first'}, status=403)
        if participation and participation.is_banned:
            return JsonResponse({'error': 'Banned from contest'}, status=403)
    elif contest.status == 'running':
        return JsonResponse({'error': 'Admin users cannot submit solutions during live contests'}, status=403)
    
    try:
        import json
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        language = data.get('language', 'cpp')
        
        if not code:
            return JsonResponse({
                'verdict': 'CE',
                'error_message': 'No code provided'
            })
        
        # Create submission
        try:
            submission = Submission.objects.create(
                user=request.user,
                problem=problem,
                code=code,
                language=language
            )
            
            # Contest problems always queued for manual processing
            return JsonResponse({
                'verdict': 'QUEUED',
                'submission_id': submission.id,
                'execution_time': 0,
                'memory_used': 0,
                'test_cases_passed': 0,
                'total_test_cases': 0,
                'error_message': None,
                'add_to_pending': True  # Signal to add to pending list
            })
        except Exception as e:
            return JsonResponse({
                'verdict': 'RE',
                'submission_id': None,
                'execution_time': 0,
                'memory_used': 0,
                'test_cases_passed': 0,
                'total_test_cases': 0,
                'error_message': f'Failed to create submission: {str(e)[:100]}'
            })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def check_solved_status(request, slug):
    """AJAX endpoint to check solved status of contest problems"""
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    contest_problems = ContestProblem.objects.filter(contest=contest).select_related('problem')
    
    # Get solved problems for the user
    solved_problem_ids = set(
        Submission.objects.filter(
            user=request.user,
            problem__in=[cp.problem for cp in contest_problems],
            verdict='AC',
            is_test=False
        ).values_list('problem_id', flat=True)
    )
    
    return JsonResponse({
        'solved_problem_ids': list(solved_problem_ids)
    })


@login_required
@user_passes_test(is_staff)
def contest_discussions_api(request, slug):
    """API endpoint to get contest discussions for admin"""
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    contest_problems = ContestProblem.objects.filter(contest=contest).select_related('problem')
    problem_ids = [cp.problem.id for cp in contest_problems]
    
    from communications.models import ProblemDiscussion
    discussions = ProblemDiscussion.objects.filter(
        problem_id__in=problem_ids
    ).select_related('user', 'problem').order_by('-created_at')[:20]
    
    discussions_data = []
    for discussion in discussions:
        discussions_data.append({
            'id': discussion.id,
            'title': discussion.title,
            'message': discussion.message,
            'user': discussion.user.username,
            'problem_title': discussion.problem.title,
            'is_resolved': discussion.is_resolved,
            'created_at': discussion.created_at.isoformat(),
            'replies_count': discussion.replies.count()
        })
    
    return JsonResponse({
        'discussions': discussions_data
    })


@login_required
@user_passes_test(is_staff)
def contest_discussions(request, slug):
    """Contest discussions management page for admin"""
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    contest_problems = ContestProblem.objects.filter(contest=contest).select_related('problem')
    problem_ids = [cp.problem.id for cp in contest_problems]
    
    from communications.models import ProblemDiscussion
    discussions = ProblemDiscussion.objects.filter(
        problem_id__in=problem_ids
    ).select_related('user', 'problem').order_by('-created_at')
    
    return render(request, 'contests/contest_discussions.html', {
        'contest': contest,
        'discussions': discussions,
        'contest_problems': contest_problems
    })


@login_required
@user_passes_test(is_staff)
def manage_announcements(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    announcements = ContestAnnouncement.objects.filter(contest=contest)
    
    if request.method == 'POST':
        form = ContestAnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.contest = contest
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, 'Announcement sent to all contestants!')
            return redirect('contests:manage_announcements', slug=slug)
    else:
        form = ContestAnnouncementForm()
    
    return render(request, 'contests/manage_announcements.html', {
        'contest': contest,
        'announcements': announcements,
        'form': form
    })


def get_contest_announcements(request, slug):
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    announcements = ContestAnnouncement.objects.filter(contest=contest)[:10]
    
    announcements_data = [{
        'id': a.id,
        'title': a.title,
        'message': a.message,
        'created_at': a.created_at.strftime('%Y-%m-%d %H:%M')
    } for a in announcements]
    
    return JsonResponse({'announcements': announcements_data})