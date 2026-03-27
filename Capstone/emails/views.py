from django.shortcuts import render, HttpResponse
from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from .models import Email
from .forms import EmailComposeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from users.models import User
from django.shortcuts import get_object_or_404, redirect
import json


class Email_Inbox_List_View(LoginRequiredMixin, ListView):
    model = Email
    template_name_suffix = '_inbox_list'
    paginate_by = 9
    paginate_orphans = 1

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        queryset = Email.objects.filter(user=user, recipients=user,
                                        archived=False).order_by('-timestamp')
        return queryset

    def get_context_data(self):
        user = self.request.user
        context = super().get_context_data()

        # Count number of unread messages and add it to the context data
        unread_messages = Email.objects.filter(
            user=user, recipients=user, archived=False, read=False).count()
        context['unread_messages'] = unread_messages
        return context


class Email_Sent_List_View(LoginRequiredMixin, ListView):
    model = Email
    template_name_suffix = '_sent_list'
    paginate_by = 9
    paginate_orphans = 1

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        queryset = Email.objects.filter(
            user=user, sender=user, archived=False).order_by('-timestamp')
        return queryset

    def get_context_data(self):
        user = self.request.user
        context = super().get_context_data()

        # Count number of unread messages and add it to the context data
        unread_messages = Email.objects.filter(
            user=user, recipients=user, archived=False, read=False).count()
        context['unread_messages'] = unread_messages
        return context


class Email_Archive_List_View(LoginRequiredMixin, ListView):
    model = Email
    template_name_suffix = '_archive_list'
    paginate_by = 9
    paginate_orphans = 1

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        queryset = Email.objects.filter(user=user, archived=True).order_by('-timestamp')
        return queryset

    def get_context_data(self):
        user = self.request.user
        context = super().get_context_data()

        # Count number of unread messages and add it to the context data
        unread_messages = Email.objects.filter(
            user=user, recipients=user, archived=False, read=False).count()
        context['unread_messages'] = unread_messages
        return context


class Email_Detail_View(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    queryset = Email.objects.all()

    def get_context_data(self, *args, **kwargs):

        # Mark email as read
        self.object.read = True
        self.object.save()
        context = super().get_context_data()
        user = self.request.user

        # Count number of unread messages and add it to the context data
        unread_messages = Email.objects.filter(
            user=user, recipients=user, archived=False, read=False).count()
        context['unread_messages'] = unread_messages
        return context

    def test_func(self):

        # User can only read his own copy of an email
        return self.get_object().user == self.request.user


class Email_Compose_View(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = EmailComposeForm(initial={'sender': self.request.user.email})
        user = self.request.user

        # Count number of unread messages
        unread_messages = Email.objects.filter(
            user=user, recipients=user, archived=False, read=False).count()
        return render(request, 'emails/email_form.html', {'form': form, 'unread_messages': unread_messages})

    def post(self, request, *args, **kwargs):
        form = EmailComposeForm(request.POST, initial={'sender': self.request.user.email})
        user = self.request.user

        # Count number of unread messages
        unread_messages = Email.objects.filter(
            user=user, recipients=user, archived=False, read=False).count()
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            body = form.cleaned_data.get('body')

            # Convert email addresses to users
            recipients = form.cleaned_data.get('recipients')
            recipients = User.objects.filter(email__in=recipients)

            # Create one email for each recipient, plus sender
            users = set()
            users.add(request.user)
            users.update(recipients)
            for user in users:
                email = Email(
                    user=user,
                    sender=request.user,
                    subject=subject,
                    body=body,
                    read=user == request.user
                )
                email.save()
                for recipient in recipients:
                    email.recipients.add(recipient)
                email.save()

                # Create variable pk to redirect user to the right copy of email
                if user == request.user:
                    pk = email.pk
            messages.success(
                request, 'Email has been sent succesfully.')
            return redirect(reverse('emails:email_details', args=[pk]))

        return render(request, 'emails/email_form.html', {'form': form, 'unread_messages': unread_messages})

    def get_context_data(self):
        user = self.request.user
        context = super().get_context_data()

        # Count number of unread messages and add it to the context data
        unread_messages = Email.objects.filter(
            user=user, recipients=user, archived=False, read=False).count()
        context['unread_messages'] = unread_messages
        return context


class Email_Reply_View(UserPassesTestMixin, Email_Compose_View):
    def get(self, request, email_pk, *args, **kwargs):
        email = get_object_or_404(Email, pk=email_pk)

        # Display error message if sender was deleted
        if not email.sender:
            messages.error(
                request, 'You can\'t reply this email. The sender doesn\'t exist.')
            return redirect(reverse('emails:email_details', args=[email_pk]))

        # Prepare data to prefill the response form
        date = email.timestamp.strftime('%B %d, %Y %H:%M %P')
        body = f'\n\n{email.sender} wrote on {date}: \n {email.body} \n\n'
        email_recipients = email.sender.email

        # Prepare subject
        # If there was more than two replies dont't change anything
        if email.subject.startswith('Re: re:'):
            subject = email.subject

        # Add 'Re: re: ' prefix if it is the second reply
        elif email.subject.startswith('Re:'):
            subject = 'Re: re: ' + email.subject.lstrip('Re: ')

        # Add Re: prefix if it is the first reply
        else:
            subject = 'Re: ' + email.subject

        # Prefill the response form
        form = EmailComposeForm(
            initial={'sender': self.request.user.email, 'recipients': email_recipients, 'subject': subject,
                     'body': body})

        # Count number of unread messages
        user = self.request.user
        unread_messages = Email.objects.filter(
            user=user, recipients=user, archived=False, read=False).count()
        return render(request, 'emails/email_form.html', {'form': form, 'unread_messages': unread_messages})

    def test_func(self):
        email = get_object_or_404(Email, pk=self.kwargs.get('email_pk'))
        # User can only reply his own copy of an email
        return email.user == self.request.user


class Email_Delete_View(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    queryset = Email.objects.all()

    def get_success_url(self):
        messages.success(
            self.request, f'The email has been deleted successfully.')
        return reverse('emails:email_inbox')

    def test_func(self):

        # User can only delete  his own copy of an email
        return self.get_object().user == self.request.user


@login_required
def update_email_archive(request):
    if request.method == 'POST':

        # Mark email as archived
        data = json.loads(request.body)
        email = get_object_or_404(Email, pk=data.get('emailpk'))

        # Check if user tries archive his own copy of email
        if email.user != request.user:
            message = f'You can only archive your own emails.'
            return JsonResponse({'message': message})
        email.archived = True
        email.save()
        message = f'The email has been archived.'
        return JsonResponse({'message': message, 'flag': 'OK'})
    message = f'Wrong request.'
    return JsonResponse({'message': message})


@login_required
def update_email_unarchive(request):
    if request.method == 'POST':

        # Mark email as unarchived
        data = json.loads(request.body)
        email = get_object_or_404(Email, pk=int(data.get('emailpk')))

        # Check if user tries unarchive his own copy of email
        if email.user != request.user:
            message = f'You can only unarchive your own emails.'
            return JsonResponse({'message': message})
        email.archived = False
        email.save()
        message = f'The email has been unarchived.'
        return JsonResponse({'message': message, 'flag': 'OK'})
    message = f'Wrong request.'
    return JsonResponse({'message': message})
