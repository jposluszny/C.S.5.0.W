from django.forms import ModelForm
from .models import Post
from django import forms


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['content']

    content = forms.CharField(
        label='New Post', widget=forms.Textarea(attrs={'class': "form-control", 'rows': 4}))
