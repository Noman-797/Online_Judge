from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from django.utils import timezone
from datetime import timedelta


class UserProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('c', 'C'),
        ('cpp', 'C++'),
        ('python', 'Python'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    solved_problems = models.IntegerField(default=0)
    total_submissions = models.IntegerField(default=0)
    bio = models.TextField(max_length=500, blank=True)
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='c')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['solved_problems']),            # Ranking queries
            models.Index(fields=['total_submissions']),          # Stats queries
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_success_rate(self):
        from submissions.models import Submission
        
        # Count unique problems solved (AC)
        solved_problems = Submission.objects.filter(
            user=self.user,
            verdict='AC',
            is_test=False
        ).values('problem').distinct().count()
        
        # Count wrong answer submissions
        wrong_answers = Submission.objects.filter(
            user=self.user,
            verdict='WA',
            is_test=False
        ).count()
        
        total_attempts = solved_problems + wrong_answers
        
        if total_attempts == 0:
            return 0
        
        return round((solved_problems / total_attempts) * 100, 2)
    
    def update_stats(self):
        """Update solved_problems and total_submissions based on actual submissions"""
        from submissions.models import Submission
        
        # Update solved problems count (unique problems with AC)
        self.solved_problems = Submission.objects.filter(
            user=self.user,
            verdict='AC',
            is_test=False
        ).values('problem').distinct().count()
        
        # Update total submissions count (exclude test submissions)
        self.total_submissions = Submission.objects.filter(
            user=self.user,
            is_test=False
        ).count()
        
        self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # Profile doesn't exist, create it
        UserProfile.objects.create(user=instance)
    except Exception as e:
        # Log error but don't break user operations
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving user profile for {instance.username}: {e}")


class OTPVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['email', 'otp', 'is_verified']), # OTP verification
        ]
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    @classmethod
    def generate_otp(cls):
        return str(random.randint(100000, 999999))