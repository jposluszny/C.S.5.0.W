from django.contrib import admin
from .models import Book, Loan, Book_Review, History

admin.site.register(Book)
admin.site.register(Loan)
admin.site.register(Book_Review)
admin.site.register(History)
