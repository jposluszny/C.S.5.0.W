from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followed = models.ManyToManyField('User', related_name='followers')


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='posts')
    created_on = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField('User', related_name='liked_posts')
    unlikes = models.ManyToManyField('User', related_name='unliked_posts')

    def __str__(self):
        return f'{self.author} {self.created_on}'
