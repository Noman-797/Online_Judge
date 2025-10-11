from django import forms
from django.utils.text import slugify
from .models import Contest, ContestProblem, ContestAnnouncement
from problems.models import Problem


class ContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ['title', 'description', 'rules', 'start_time', 'end_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
            'rules': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
            'start_time': forms.DateTimeInput(attrs={'class': 'input input-bordered w-full', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'input input-bordered w-full', 'type': 'datetime-local'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Auto-generate slug from title
        base_slug = slugify(instance.title)
        slug = base_slug
        counter = 1
        while Contest.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        instance.slug = slug
        
        # Auto-calculate duration in minutes
        if instance.start_time and instance.end_time:
            duration_seconds = (instance.end_time - instance.start_time).total_seconds()
            instance.duration = int(duration_seconds / 60)
        
        if commit:
            instance.save()
        return instance


class ContestProblemForm(forms.ModelForm):
    problem = forms.ModelChoiceField(
        queryset=Problem.objects.filter(is_active=True, contest_only=True),
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'}),
        help_text="Only contest-only problems (hidden from public list) are shown",
        empty_label="Select Problem"
    )
    
    class Meta:
        model = ContestProblem
        fields = ['problem', 'order', 'points']
        widgets = {
            'order': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'points': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Mark the problem as contest_only when added to a contest
        if instance.problem:
            instance.problem.contest_only = True
            instance.problem.save()
        
        if commit:
            instance.save()
        return instance


class ContestAnnouncementForm(forms.ModelForm):
    class Meta:
        model = ContestAnnouncement
        fields = ['title', 'message']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'message': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
        }