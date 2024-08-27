from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from PIL import Image


class User(AbstractUser):
    staff_member = models.BooleanField(default=False, blank=True)
    born = models.DateField(null=True, blank=True)
    address = models.TextField(max_length=511)
    profile_picture = models.ImageField(default='default.jpeg', upload_to='profile_pictures')
    telefon_number = models.CharField(max_length=9)
    email = models.EmailField(unique=True)

    def get_absolute_url(self):
        return reverse('users:profile', args=[self.pk])
    
    def save(self, *args, **kwargs):
        ''' Resizes big images '''

        super().save()
        img = Image.open(self.profile_picture.path)
        if img.height > 300 or img.width > 300:
            img.thumbnail((300,300))
            img.save(self.profile_picture.path)

