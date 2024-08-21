from django.shortcuts import render, HttpResponse
from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from .models import Book, Loan, Book_Review, History
from emails.models import Email
from users.models import User
from django.shortcuts import get_object_or_404, redirect
from .forms import File_Book_Add_Form, BookForm
import csv
import json
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Value
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Avg, Max, Min, Sum, Count
from django.db import transaction
import datetime
from django.views.generic.base import TemplateView, RedirectView
from django import forms


class Home_List_View(LoginRequiredMixin, View):
    template_name = 'library/home.html'

    def get(self, request, *args, **kwargs):

        # Get data displayed on user dashbord - user list is loaded via post method
        pending_requests = Loan.objects.filter(status='pending')
        loans = Loan.objects.filter(status='accepted')
        overdue_loans = Loan.objects.filter(return_date__lt=datetime.date.today())
        user = request.user

        # Count number of unread messages
        unread_messages = Email.objects.filter(
            user=user, recipients=user, archived=False, read=False).count()
        data = {'pending_requests': pending_requests, 'loans': loans,
                'overdue_loans': overdue_loans, 'unread_messages': unread_messages}
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = json.loads(request.body)

        # For staff members user list on dashbord is loaded and filtered dynamically using javascript
        if user.staff_member:
            query = data.get('parameter')
            if query == '':

                # If no query display all users
                users = User.objects.all().order_by('username')
            else:

                # Get users whose names start with query
                users = User.objects.filter(username__istartswith=query).order_by('username')
            data = [{'user_pk': i.pk, 'username': i.username, 'total': i.borrowing.count(), 'last_login': i.last_login,
                     'email': i.email} for i in users]
            return JsonResponse({'data': data})
        else:

            # For none staff members order loans by requested parameter
            loans = user.borrowing.all().order_by(data.get('parameter'))
            result = [{'loan_pk': i.pk, 'book_title': i.book.title,
                       'status': i.status, 'return_date': i.return_date, 'is_overdue': i.is_overdue} for i in loans]
        return JsonResponse({'data': result})


class Search_List_View(View):
    template_name = 'library/search_list.html'

    def get(self, request):
        ''' Searches the database and paginates the results '''

        query = request.GET.get('q')

        # Display message if user tries to access the page directly
        if query == None:
            messages.info(
                request, 'Enter a query to get results.')
            return render(request, self.template_name)

        # Search books by the ISBN number, the title of a book, or the author of a book
        queryset = Book.objects.filter(
            title__icontains=query) | Book.objects.filter(author__icontains=query) | Book.objects.filter(isbn__icontains=query)
        if not queryset:
            messages.info(
                request, f'There are no results for "{query}".')

        # Create pagination
        page_nr = request.GET.get('page', 1)
        paginator = Paginator(queryset, 5)
        page_obj = paginator.page(page_nr)
        return render(request, self.template_name, {'page_obj': page_obj})


class Book_Add_View(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Book
    form_class = BookForm

    def test_func(self):

        # Only staff members can delete books
        return self.request.user.staff_member

    def get_success_message(self, cleaned_data):
        title = cleaned_data.get('title')
        return f'Book "{title}" has been added successfully.'


class File_Book_Add_View(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        form = File_Book_Add_Form()
        return render(request, 'library/file_book_form.html', {'form': form})

    def post(self, request):
        ''' Reads csv file and adds books to the database'''

        form = File_Book_Add_Form(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Read lines of csv file
                file = form.cleaned_data.get('file')
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)

                # Read each line and get values needed to create book object
                for isbn, title, author, year in reader:

                    try:
                        book = Book.objects.create(isbn=isbn, title=title,
                                                   author=author, year=year)

                    # If object can not be save create error message
                    except Exception as e:
                        messages.error(
                            request, f'Book {isbn} {title} by {author} was NOT ADDED! "{e}"')

            # If there is a problem with file format create error message
            except Exception as e:
                messages.error(request, e)

            # If there are no errors create success message
            if not messages.get_messages(request):
                messages.success(request, 'Books were added successfully!')
            return redirect(reverse('library:file_add_book'))
        return render(request, 'library/file_book_form.html', {'form': form})

    def test_func(self):

        # Only staff members can delete books
        return self.request.user.staff_member


class Book_Detail_View(DetailView):
    queryset = Book.objects.all()


class Book_Delete_View(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    queryset = Book.objects.all()

    def delete(self, request, *args, **kwargs):
        # Book must be returned before deletion
        if Loan.objects.filter(book__pk=kwargs.get('pk')):
            messages.error(
                self.request, 'You can not delete a lent book.')
            return redirect(reverse('library:book_details', args=[kwargs.get('pk')]))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(
            self.request, f'Book "{self.get_object().title}" by {self.get_object().author} has been deleted successfully.')
        return reverse('library:home')

    def test_func(self):

        # Only staff members can delete books
        return self.request.user.staff_member


class Book_Update_View(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    template_name = 'library/book_update_form.html'
    queryset = Book.objects.all()
    fields = '__all__'
    success_message = 'Book "%(title)s" has been updated successfully.'

    def test_func(self):

        # Only staff members can update books
        return self.request.user.staff_member


class Loan_Detail_View(LoginRequiredMixin, DetailView):
    queryset = Loan.objects.all()


class Loan_Delete_View(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    queryset = Loan.objects.all()

    def get_success_url(self):
        messages.success(
            self.request, f'The request for "{self.get_object().book.title}" requested by "{self.get_object().user.username}" has been deleted successfully.')
        return reverse('users:profile', kwargs={'pk': self.get_object().user.pk})

    def test_func(self):

        # Only staff members can delete loans
        return self.request.user.staff_member


class Loan_Update_View(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'library/loan_update_form.html'
    queryset = Loan.objects.all()
    fields = '__all__'

    def get_success_url(self):
        messages.success(
            self.request, f'The request for "{self.get_object().book.title}" requested by "{self.get_object().user.username}" has been updated successfully.')
        return reverse('library:loan_details', kwargs={'pk': self.get_object().pk})

    def test_func(self):

        # Only staff members can update loans
        return self.request.user.staff_member


class History_Detail_View(DetailView):
    queryset = History.objects.all()


class User_Reviews(LoginRequiredMixin, ListView):
    model = Book_Review
    template_name = 'library/user_reviews.html'
    paginate_by = 4
    paginate_orphans = 1

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return user.reviews.all()

    def get_context_data(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        context = super().get_context_data()
        context['author'] = user
        return context


@ login_required
def borrow_book(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        book = get_object_or_404(Book, pk=data.get('pk'))
        user = request.user
        message = ''

        # Check if book is available
        loan_query = Loan.objects.filter(book=book)
        if loan_query.count() > 0:
            message = f'The book \"{book.title}\" by {book.author} is not available.'
            return JsonResponse({'message': message})

        # Only 10 books per user is allowed
        if user.borrowing.count() >= 10:
            message = f'User \"{request.user}\" has already borrowed the maximum number of books.'
            return JsonResponse({'message': message})
        else:

            # Create and save new loan
            loan = Loan(book=book, user=request.user, status='pending')
            loan.save()
            message = f'You have requested \"{book.title}\" by {book.author}. Your request is waiting for approval.'
            data = {'message': message, 'flag': 'ok'}
            if user.staff_member:
                data['loan_pk'] = loan.pk
            return JsonResponse(data)

    messages.error(request, 'Wrong request.')
    return redirect(reverse('library:home'))


@ login_required
@ user_passes_test(lambda user: user.staff_member)
def accept_request(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        book = get_object_or_404(Book, pk=int(data.get('bookpk')))
        loan_query = Loan.objects.filter(book=book)

        # Ensure that only one loan exists
        if loan_query.count() == 1 and loan_query.get().status == 'pending':

            # Update status to accepted end set can_renew attribute to true
            loan = loan_query.get()
            loan.status = 'accepted'
            loan.loan_date = datetime.date.today()
            loan.return_date = loan.loan_date + datetime.timedelta(28)
            loan.can_renew = True
            loan.save()
            message = f'{loan} has been accepted.'
            return JsonResponse({'message': message, 'flag': 'OK', 'owner_pk': loan.user.pk, 'owner': loan.user.username, 'loan_date': loan.loan_date, 'return_date': loan.return_date})
        elif loan_query.count() == 0:

            # Dispalay error message if there is no request
            message = f'There is no such request for "{book.title}" by {book.author}.'
            return JsonResponse({'message': message})

        elif loan_query.get().status != 'pending':

            # Dispalay error message if request status is not pending
            message = f'There is no pending request for "{book.title}" by {book.author}.'
            return JsonResponse({'message': message})
        else:
            # Dispalay error message if there is more than one request
            message = f'Something went wrong.'
            return JsonResponse({'message': message})

    messages.error(request, 'Wrong request.')
    return redirect(reverse('library:home'))


@ login_required
@ user_passes_test(lambda user: user.staff_member)
def return_book(request):
    if request.method == 'POST':
        user = request.user
        data = request.POST
        book = get_object_or_404(Book, pk=data.get('bookpk'))
        loan_query = Loan.objects.filter(book=book)

        # Ensure that only one loan exists with status accepted
        if loan_query.count() == 1 and loan_query.get().status == 'accepted':
            loan = loan_query.get()
            loan.delete()
            message = f'The book \"{book.title}\" by {book.author} has been returned.'
            messages.success(request, message)
            return redirect(reverse('library:book_details', kwargs={'pk': loan.book.pk}))
        elif loan_query.count() == 0:

            # Dispalay error message if there is no loan
            message = f'There is no such request for \"{book.title}\" by {book.author}.'
            messages.error(request, message)
            return redirect(reverse('library:home'))
        elif loan_query.get().status != 'accepted':

            # Dispalay error message if request was not accepted
            message = f'The request has not been accepted.'
            messages.error(request, message)
            return redirect(reverse('library:home'))
        else:

            # Dispalay error message if there is more than one loan
            message = f'Something went wrong.'
            messages.error(request, message)
            return redirect(reverse('library:home'))

    messages.error(request, 'Wrong request.')
    return redirect(reverse('library:home'))


@ login_required
@ user_passes_test(lambda user: user.staff_member)
def reject_request(request):
    if request.method == 'POST':
        user = request.user
        data = request.POST
        book = get_object_or_404(Book, pk=data.get('bookpk'))
        loan_query = Loan.objects.select_for_update().filter(book=book)
        if loan_query.count() == 1 and loan_query.get().status == 'pending':
            # Get reason of rejection
            reject_message = data.get('rejectMessage')

            # Use transaction to ensure that history object was created and loan was deleted
            with transaction.atomic():
                loan = loan_query.get()
                loan.status = 'rejected'
                loan.save()
                loan.delete()
                History.objects.create(
                    book=loan.book, user=loan.user,
                    fee=loan.fee,  status=loan.status, can_renew=loan.can_renew,
                    is_overdue=loan.is_overdue, reject_message=f'"{reject_message}"')
            message = f'The request for the book \"{book.title}\" by the user \"{loan.user.username}\" has been rejected.'
            messages.success(request, message)
            return redirect(reverse('library:book_details', kwargs={'pk': loan.book.pk}))
        elif loan_query.count() == 0:

            # Dispalay error message if there is no request
            message = f'There is no such request for \"{book.title}\" by {book.author}.'
            messages.error(request, message)
            return redirect(reverse('library:home'))
        elif loan_query.get().status != 'pending':
            # Dispalay error message if status of request is not pending
            message = f'There is no pending request for \"{book.title}\" by {book.author}.'
            messages.error(request, message)
            return redirect(reverse('library:home'))
        else:
            # Dispalay error message if there is more than one request
            message = f'Something went wrong.'
            messages.error(request, message)
        return redirect(reverse('library:home'))

    messages.error(request, 'Wrong request.')
    return redirect(reverse('library:home'))


@ login_required
def renew_book(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        book = get_object_or_404(Book, pk=int(data.get('pk')))
        loan_query = Loan.objects.filter(book=book)

        # Ensure that only one loan exists with status accepted
        if loan_query.count() == 1 and loan_query.get().status == 'accepted':
            loan = loan_query.get()

            # Book can be renewed only once
            if loan.can_renew == False:
                message = f'You can not renew the book "{book.title}" by {book.author} twice. It has been already renewed.'
                return JsonResponse({'message': message})

            # Book can renew only the book owner
            if request.user != loan.user:
                message = f'You are not allowed to renew the book "{book.title}" by {book.author}.'
                return JsonResponse({'message': message})

            # Calculate new return date and set can_renew attribute to false
            return_date = loan.return_date + datetime.timedelta(14)
            loan.return_date = return_date
            loan.can_renew = False
            loan.save()
            message = f'The book \"{book.title}\" by {book.author} has been renewed.'
            return JsonResponse({'message': message, 'flag': 'ok', 'return_date': return_date})
        elif loan_query.count() == 0:

            # Dispalay error message if there is no loan
            message = f'There is no such request for \"{book.title}\" by {book.author} and user {user}.'
            return JsonResponse({'message': message})

        elif loan_query.get().status != 'accepted':

            # Dispalay error message if there is no accepted request
            message = f'There is no such accepted request for \"{book.title}\" by {book.author} and user {user}.'
            return JsonResponse({'message': message})
        else:
            # Return error message if there is more than one request
            message = f'Something went wrong.'
            return JsonResponse({'message': message})

    messages.error(request, 'Wrong request.')
    return redirect(reverse('library:home'))


@ login_required
def add_review(request):
    if request.method == 'POST':

        # Get the needed data to create and save review
        data = json.loads(request.body)
        book = get_object_or_404(Book, pk=data.get('bookPk'))
        content = data.get('content')
        review = Book_Review(book=book, author=request.user, content=content)
        review.save()

        # Prepare data to create response
        response = Book_Review.objects.values().get(pk=review.pk)
        response['author__username'] = review.author.username
        return JsonResponse(response)
    messages.error(request, 'Wrong request.')
    return redirect(reverse('library:home'))


def load_reviews(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.values('author_id', 'author__username',
                                  'creation_date', 'content', 'id')
    return JsonResponse(list(reviews), safe=False)


@ login_required
def edit_review(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        review = get_object_or_404(Book_Review, pk=data.get('id'))

        # Check if the currently logged user is the author of the review
        if request.user != review.author:
            return HttpResponse(status=403)
        review.content = data.get('content')
        review.save()

        # Prepare data to create response
        response = Book_Review.objects.values().get(pk=review.pk)
        response['author__username'] = review.author.username
        return JsonResponse(response)
    messages.error(request, 'Wrong request.')
    return redirect(reverse('library:home'))


@ login_required
def del_review(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        review = get_object_or_404(Book_Review, pk=data.get('id'))

        # Check if the currently logged user is the author of the review
        if request.user != review.author:
            return HttpResponse(status=403)
        id = review.pk
        review.delete()
        return JsonResponse({'id': id})
    messages.error(request, 'Wrong request.')
    return redirect(reverse('library:home'))
