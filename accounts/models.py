from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from django.utils import timezone
from datetime import timedelta


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    solved_problems = models.IntegerField(default=0)
    total_submissions = models.IntegerField(default=0)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['solved_problems']),            # Ranking queries
            models.Index(fields=['total_submissions']),          # Stats queries
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_success_rate(self):
        if self.total_submissions == 0:
            return 0
        return round((self.solved_problems / self.total_submissions) * 100, 2)


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