from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.utils._os import safe_join
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm
from submissions.models import Submission
from .models import OTPVerification
from django.core.mail import send_mail
from django.conf import settings


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = OTPVerification.generate_otp()
            OTPVerification.objects.create(email=email, otp=otp)
            
            # Send OTP email
            try:
                send_mail(
                    'OTP Verification - All About Semicolons',
                    f'Your OTP code is: {otp}\n\nThis code will expire in 10 minutes.\n\nIf you did not request this, please ignore this email.',
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@semicolons.com',
                    [email],
                    fail_silently=False,
                )
                if settings.DEBUG:
                    print(f'OTP for {email}: {otp}')  # Debug print only in development
            except Exception as e:
                messages.error(request, 'Failed to send OTP email. Please try again.')
                return render(request, 'accounts/register.html', {'form': form})
            
            request.session['registration_data'] = form.cleaned_data
            messages.success(request, 'OTP sent to your email. Please verify to complete registration.')
            return redirect('accounts:verify_otp')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    # Get solved problems
    solved_problem_ids = Submission.objects.filter(
        user=request.user, 
        verdict='AC'
    ).values_list('problem', flat=True).distinct()
    
    from problems.models import Problem
    solved_problems = Problem.objects.filter(id__in=solved_problem_ids)[:10]
    solved_problems_count = solved_problem_ids.count()
    
    # Calculate stats
    total_submissions = Submission.objects.filter(user=request.user).count()
    accepted_submissions = Submission.objects.filter(user=request.user, verdict='AC').count()
    
    # Update user profile with proper error handling
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        from .models import UserProfile
        profile = UserProfile.objects.create(user=request.user)
    except Exception as e:
        messages.error(request, 'Error accessing profile data.')
        from .models import UserProfile
        profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    profile.solved_problems = solved_problems_count
    profile.total_submissions = total_submissions
    profile.save()
    
    stats = {
        'total_submissions': total_submissions,
        'accepted_submissions': accepted_submissions,
        'solved_problems': solved_problems_count,
        'success_rate': profile.get_success_rate(),
    }
    
    # Add admin statistics if user is staff
    admin_stats = {}
    if request.user.is_staff:
        from problems.models import Problem, Category
        admin_stats = {
            'problems_created': Problem.objects.filter(created_by=request.user).count(),
            'total_problems': Problem.objects.count(),
            'total_categories': Category.objects.count(),
        }
    
    context = {
        'solved_problems': solved_problems,
        'stats': stats,
        'admin_stats': admin_stats,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    from .models import UserProfile
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)
        except Exception:
            user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
        
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)
        except Exception:
            user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
        
        profile_form = UserProfileForm(instance=user_profile)
    
    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        registration_data = request.session.get('registration_data')
        
        if not registration_data:
            messages.error(request, 'Registration session expired. Please register again.')
            return redirect('accounts:register')
        
        otp_obj = OTPVerification.objects.filter(
            email=registration_data['email'], 
            otp=otp, 
            is_verified=False
        ).first()
        
        if otp_obj and not otp_obj.is_expired():
            try:
                form = CustomUserCreationForm(registration_data)
                if form.is_valid():
                    user = form.save()
                    from .models import UserProfile
                    if not hasattr(user, 'userprofile'):
                        UserProfile.objects.create(user=user)
                    
                    otp_obj.is_verified = True
                    otp_obj.save()
                    
                    login(request, user)
                    del request.session['registration_data']
                    messages.success(request, f'Welcome {user.first_name}! Registration successful!')
                    return redirect('home')
            except Exception as e:
                messages.error(request, 'Registration failed. Please try again.')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
    
    return render(request, 'accounts/verify_otp.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


def user_profile(request, username):
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User
    from .models import UserProfile
    
    # Validate username to prevent path traversal
    if not username.isalnum() and '_' not in username and '-' not in username:
        messages.error(request, 'Invalid username format.')
        return redirect('home')
    
    user = get_object_or_404(User, username=username)
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    # Get user's submission stats
    total_submissions = Submission.objects.filter(user=user).count()
    accepted_submissions = Submission.objects.filter(user=user, verdict='AC').count()
    
    success_rate = 0
    if total_submissions > 0:
        success_rate = round((accepted_submissions / total_submissions) * 100, 1)
    
    context = {
        'profile_user': user,
        'profile': profile,
        'total_submissions': total_submissions,
        'accepted_submissions': accepted_submissions,
        'success_rate': success_rate,
    }
    
    return render(request, 'accounts/user_profile.html', context)