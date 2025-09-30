from django.db import models
from django.contrib.auth.models import User
from problems.models import Problem


class Submission(models.Model):
    LANGUAGE_CHOICES = [
        ('c', 'C'),
        ('cpp', 'C++'),
        ('python', 'Python'),
    ]
    # Note: PythonAnywhere only supports Python
    # For C/C++ support, use Railway/Render/DigitalOcean
    
    VERDICT_CHOICES = [
        ('QUEUED', 'Queued'),
        ('JUDGING', 'Judging'),
        ('AC', 'Accepted'),
        ('WA', 'Wrong Answer'),
        ('CE', 'Compilation Error'),
        ('RE', 'Runtime Error'),
        ('TLE', 'Time Limit Exceeded'),
        ('MLE', 'Memory Limit Exceeded'),
        ('PE', 'Presentation Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    code = models.TextField()
    verdict = models.CharField(max_length=10, choices=VERDICT_CHOICES, default='QUEUED')
    execution_time = models.FloatField(null=True, blank=True)  # in seconds
    memory_used = models.IntegerField(null=True, blank=True)  # in KB
    compilation_error = models.TextField(blank=True)
    runtime_error = models.TextField(blank=True)
    test_cases_passed = models.IntegerField(default=0)
    total_test_cases = models.IntegerField(default=0)
    is_test = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    judged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['user', '-submitted_at']),      # User submissions
            models.Index(fields=['problem', '-submitted_at']),   # Problem submissions
            models.Index(fields=['verdict']),                    # Verdict filtering
            models.Index(fields=['user', 'problem', 'verdict']), # User problem status
            models.Index(fields=['submitted_at']),               # Time-based queries
            models.Index(fields=['user', 'verdict']),            # User stats
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.verdict}"
    
    def get_verdict_display_class(self):
        verdict_classes = {
            'QUEUED': 'text-blue-500',
            'JUDGING': 'text-yellow-500',
            'AC': 'text-green-600',
            'WA': 'text-red-600',
            'CE': 'text-yellow-600',
            'RE': 'text-orange-600',
            'TLE': 'text-purple-600',
            'MLE': 'text-blue-600',
            'PE': 'text-gray-600',
        }
        return verdict_classes.get(self.verdict, 'text-gray-500')
    
    @property
    def error_message(self):
        """Get appropriate error message based on verdict"""
        if self.verdict == 'QUEUED':
            return 'Submission is queued for evaluation'
        elif self.verdict == 'JUDGING':
            return 'Submission is being evaluated'
        elif self.verdict == 'CE' and self.compilation_error:
            return self.compilation_error
        elif self.verdict == 'RE' and self.runtime_error:
            return self.runtime_error
        elif self.verdict == 'TLE':
            return f'Time limit exceeded ({self.problem.time_limit}s)'
        elif self.verdict == 'MLE':
            return f'Memory limit exceeded ({self.problem.memory_limit}MB)'
        elif self.verdict == 'WA':
            return 'Wrong answer - output does not match expected result'
        elif self.verdict == 'PE':
            return 'Presentation error - output format is incorrect'
        elif self.verdict == 'AC':
            return 'Accepted - All test cases passed'
        return None