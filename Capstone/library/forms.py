from .models import Book, Loan
from django import forms
from users.models import User
from django.core import validators
import datetime


class BookForm(forms.ModelForm):
    isbn = forms.IntegerField(validators=[validators.MaxValueValidator(
        9999999999)])
    year = forms.IntegerField(
        validators=[validators.MaxValueValidator(datetime.date.today().year)])

    class Meta:
        model = Book
        fields = '__all__'


class File_Book_Add_Form(forms.Form):
    file = forms.FileField(label=False,
                           widget=forms.FileInput(attrs={'class': "form-control",
                                                         'id': "inputGroupFile04", 'aria-describedby': "inputGroupFileAddon04",
                                                         'aria-label': "Upload"}))
