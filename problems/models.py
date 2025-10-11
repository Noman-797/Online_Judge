from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    constraints = models.TextField(blank=True)
    sample_input = models.TextField()
    sample_output = models.TextField()
    sample_note = models.CharField(max_length=500, blank=True, help_text="Optional explanation for sample input/output")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    time_limit = models.IntegerField(default=2)  # seconds
    memory_limit = models.IntegerField(default=128)  # MB
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    contest_only = models.BooleanField(default=False, help_text="Hide from public problem list, show only in contests")
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['is_active', 'contest_only']),  # Problem list filtering
            models.Index(fields=['category', 'difficulty']),     # Category + difficulty filtering
            models.Index(fields=['created_at']),                 # Ordering
            models.Index(fields=['slug']),                       # URL lookups
            models.Index(fields=['created_by']),                 # Admin queries
        ]
    
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)
    note = models.CharField(max_length=200, blank=True, help_text="Optional note for this test case")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['problem', 'is_sample']),       # Problem test cases
        ]
    
    def __str__(self):
        return f"Test case for {self.problem.title}"