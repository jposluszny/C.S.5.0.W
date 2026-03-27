from .models import Email
from django import forms
from users.models import User
from django.core import validators


class MultiEmailField(forms.Field):
    def to_python(self, value):

        # Return an empty list if no input was given.
        if not value:
            return []
        return [i.strip() for i in value.split(',')]

    def validate(self, value):
        # Use the parent's handling of required field.
        super().validate(value)
        for email in value:
            validators.validate_email.message = f'"{email}" is not a valid email address.'
            validators.validate_email(email)


class EmailComposeForm(forms.Form):
    sender = forms.CharField(max_length=254)
    recipients = MultiEmailField()
    subject = forms.CharField(required=False, max_length=1000)
    body = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 5, 'rows': 5}))

    sender.widget.attrs.update({'readonly': True})

    def clean_recipients(self, *args, **kwargs):

        # Check if there is a user with a given email
        recipients = self.cleaned_data.get('recipients')
        users_emails = User.objects.values_list('email', flat=True).all()
        for i in recipients:
            if i not in users_emails:
                raise forms.ValidationError(f'There is no user with such an email address: {i}.')
        return recipients
