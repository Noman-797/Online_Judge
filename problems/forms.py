from django import forms
from .models import Problem, Category, TestCase


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'slug', 'description', 'input_format', 'output_format', 
                 'constraints', 'sample_input', 'sample_output', 'difficulty', 
                 'time_limit', 'memory_limit', 'category', 'tags', 'contest_only']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter problem title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'problem-slug'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'input_format': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'output_format': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'constraints': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sample_input': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sample_output': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2.0'}),
            'memory_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '256'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'arrays, sorting, dynamic programming'}),
            'contest_only': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = ['input_data', 'expected_output', 'is_sample']
        widgets = {
            'input_data': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
            'expected_output': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4}),
            'is_sample': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
        }