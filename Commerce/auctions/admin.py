from django.contrib import admin
from .models import Listing, Bid, User, Comment

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
