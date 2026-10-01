from django import forms
from .models import Dataset, Project

class ProjectForm(forms.ModelForm):
    """Form to create or edit a project."""
    class Meta:
        model = Project
        fields = ['title', 'description']
        labels = {
            'title': 'Project Title',
            'description': 'Project Description',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter project title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter project description', 'rows': 3}),
        }


class DatasetForm(forms.ModelForm):
    """Form to add a new dataset with a GEO ID."""
    geo_id = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter GEO ID (e.g., GSE12345)',
        }),
        label='GEO ID',
    )

    class Meta:
        model = Dataset
        fields = ['name', 'description', 'geo_id']
        labels = {
            'name': 'Dataset Name',
            'description': 'Dataset Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter dataset name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter dataset description', 'rows': 3}),
        }