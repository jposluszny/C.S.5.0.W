from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', related_name='watchlist')
    wins = models.ManyToManyField('Listing', related_name='wins')


class Listing(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=7, decimal_places=2)
    url = models.URLField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=300, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.title} ${self.starting_bid}'


class Bid(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=7, decimal_places=2)
    created = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.listing.title} ${self.bid}'


class Comment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user} on ${self.created}'
