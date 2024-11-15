from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Blog(models.Model):
    title=models.CharField(max_length=50)
    date=models.DateTimeField(null=False, default=datetime.today)
    content=models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs")

    def __str__(self):
        return self.title
    

