from django import forms
from . import util
from django.core.exceptions import ValidationError


class Entry_Form(forms.Form):
    """ Form used for creating new entries """

    title = forms.CharField(label="Title", max_length=100,
                 widget=forms.TextInput(attrs={"class":"form-control"}))
    content = forms.CharField(label="Content",
                              widget=forms.Textarea(attrs={"rows": "10", "class":"form-control"}))
    def clean_title(self):
        """ Validates entries. If title already exists, raises  validation error """

        title = self.cleaned_data["title"]
        entries = util.list_entries()
        if title in entries:
            raise ValidationError(f"Entry \"{title}\" already exists in the encyclopedia!")
        return title
    
class Edit_Entry_Form(forms.Form):
    """ Form used for editing entries """

    title = forms.CharField(label="Title", disabled=True, required=False, max_length=100,
                 widget=forms.TextInput(attrs={"class":"form-control"}))
    content = forms.CharField(label="Content",
                              widget=forms.Textarea(attrs={"rows": "10", "class":"form-control"}))


