from django import forms
from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['language', 'code']
        widgets = {
            'language': forms.Select(attrs={'class': 'select select-bordered w-full mb-4'}),
            'code': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full font-mono text-sm',
                'rows': 20,
                'placeholder': '#include <stdio.h>\n\nint main() {\n    // Your code here\n    return 0;\n}'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['language'].empty_label = "Select Language"