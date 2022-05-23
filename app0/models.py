from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, default="0")
    photo = models.URLField(blank=True)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


'''
class Menber(AbstractUser):
    data0 = models.CharField(max_length=100)

    def __str__(self):
        return self.username
'''
