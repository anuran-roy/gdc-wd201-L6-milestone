from django.db import models

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Task(models.Model):
    priority = models.IntegerField(validators=[MinValueValidator(1)])
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        # unique_together = (("user", "priority", "completed"),)
        ordering = ["priority"]
