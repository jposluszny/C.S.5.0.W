from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import UserRegistrationForm, UserUpdateForm
from .models import User
from library.models import History
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
import json
from django.http import JsonResponse
from django.db.models import Sum


class User_Registration_View(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/user_form.html'

    def test_func(self):

        # Only staff members can register new users
        return self.request.user.staff_member

    def get_success_message(self, cleaned_data):
        user_name = cleaned_data.get('username')
        return f'User "{user_name}" has been created succesfully.'


class User_Update_View(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = UserUpdateForm
    queryset = User.objects.all()
    template_name_suffix = '_update_form'

    def test_func(self):

        # Only staff members can update users' profiles
        return self.request.user.staff_member

    def get_success_message(self, cleaned_data):
        user_name = cleaned_data.get('username')
        return f'User has been updated succesfully.'


class User_Detail_View(LoginRequiredMixin, DetailView):
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        ''' Each call return 5 books from history '''

        user = get_object_or_404(User, pk=kwargs.get('pk'))
        data = json.loads(request.body)

        # Get start index of a new group of books
        start = int(data.get('start'))

        # Get 5 more books
        books = user.history_borrowing.order_by(
            '-loan_date').order_by('-pk')[start:start + 5]

        # Return 5 more books
        if books:
            response = [{'book_pk': i.book.pk, 'book_title': i.book.title, 'book_author': i.book.author,
                         'loan_date': i.loan_date, 'return_date': i.return_date,
                         'status': i.status, 'loan_pk': i.pk} for i in books]
        else:
            # Return none if user reaches end of history
            response = None

        return JsonResponse({'response': response})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = kwargs.get('object')

        # Sum up all fees user must pay
        fees_to_pay = sum([i.fee for i in user.borrowing.all()])

        # Sum up all fees user has already paid
        paid_fees = user.history_borrowing.aggregate(fees=Sum('fee')).get('fees')
        if not paid_fees:
            paid_fees = 0

        # Add to context all fees user got and fees he must pay
        context['fees_to_pay'] = fees_to_pay
        context['total_fees'] = paid_fees + fees_to_pay
        return context


class User_Delete_View(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        user = self.get_object()

        # Only user who has returned all books can be deleted
        if user.borrowing.all():
            messages.error(request, f'You can\'t delete users who have borrowed books.')
            return redirect(reverse('users:profile', args=[user.pk]))
        return super().post(request)

    def get_success_url(self):
        messages.success(self.request, f'User "{self.object}" has been deleted succesfully!')
        return reverse('library:home')

    def test_func(self):
        # Only staff members can delete users
        return self.request.user.staff_member


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):

    def get_success_url(self):
        return reverse('users:password_change_done')
