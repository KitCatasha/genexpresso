from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    """A project created by the user."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Dataset(models.Model):
    """A dataset tied to a specific project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # Links to a project
    name = models.CharField(max_length=200)  # Dataset name
    description = models.TextField(blank=True)  # Dataset description
    geo_id = models.CharField(max_length=50, default='unknown')  # GEO ID for dataset
    date_added = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"{self.name} (GEO ID: {self.geo_id})"
