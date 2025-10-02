from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes and placeholders
        self.fields['username'].widget.attrs.update({
            'class': 'input input-bordered w-full focus:border-secondary focus:ring-2 focus:ring-secondary/20 transition-all duration-300 hover:border-secondary/50',
            'placeholder': 'Choose a username'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'input input-bordered w-full focus:border-secondary focus:ring-2 focus:ring-secondary/20 transition-all duration-300 hover:border-secondary/50',
            'placeholder': 'John'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'input input-bordered w-full focus:border-secondary focus:ring-2 focus:ring-secondary/20 transition-all duration-300 hover:border-secondary/50',
            'placeholder': 'Doe'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'input input-bordered w-full focus:border-secondary focus:ring-2 focus:ring-secondary/20 transition-all duration-300 hover:border-secondary/50',
            'placeholder': 'Enter your email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'input input-bordered w-full focus:border-secondary focus:ring-2 focus:ring-secondary/20 transition-all duration-300 hover:border-secondary/50',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'input input-bordered w-full focus:border-secondary focus:ring-2 focus:ring-secondary/20 transition-all duration-300 hover:border-secondary/50',
            'placeholder': 'Confirm your password'
        })
    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        
        # Check if email is Gmail
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Only Gmail addresses are allowed for registration.")
        
        # Check for duplicate email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        
        return email
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4})
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        
        # Check if email is Gmail
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Only Gmail addresses are allowed.")
        
        # Check for duplicate email (exclude current user)
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already registered.")
        
        return email