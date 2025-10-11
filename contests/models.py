from django.db import models
from django.contrib.auth.models import User
from problems.models import Problem
from django.utils import timezone


class Contest(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('running', 'Running'),
        ('ended', 'Ended'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    rules = models.TextField(blank=True, help_text="Contest rules and guidelines")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    problems = models.ManyToManyField(Problem, through='ContestProblem')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active', '-start_time']),   # Contest listing
            models.Index(fields=['start_time', 'end_time']),     # Status queries
            models.Index(fields=['slug']),                       # URL lookups
            models.Index(fields=['created_by']),                 # Admin queries
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return 'upcoming'
        elif now <= self.end_time:
            return 'running'
        else:
            return 'ended'
    
    def can_participate(self, user):
        return self.status == 'running' and user.is_authenticated


class ContestProblem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    points = models.IntegerField(default=100)
    
    class Meta:
        ordering = ['order']
        unique_together = ['contest', 'problem']
        indexes = [
            models.Index(fields=['contest', 'order']),           # Contest problems
        ]


class ContestParticipation(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    total_score = models.IntegerField(default=0)
    problems_solved = models.IntegerField(default=0)
    is_banned = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['contest', 'user']
        indexes = [
            models.Index(fields=['contest', '-total_score']),    # Leaderboard
            models.Index(fields=['user']),                       # User contests
        ]
    
    def save(self, *args, **kwargs):
        # Prevent admin users from participating
        if self.user.is_staff or self.user.is_superuser:
            raise ValueError("Admin users cannot participate in contests")
        super().save(*args, **kwargs)


class ContestAnnouncement(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contest.title}: {self.title}"