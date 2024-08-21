from django.test import TestCase
from .models import Loan, Book, History, Book_Review
from users.models import User
import datetime
from django.test import Client
from django.urls import reverse
from django.db.models import Avg, Max, Min, Sum, Count
import json
from django.test import tag
import datetime


class LibraryTestCase(TestCase):
    def setUp(self):
        # Create client object as attribute
        self.client = Client()

        # Create books
        book1 = Book.objects.create(isbn=1, title='a', author='bj', year=2000)
        book2 = Book.objects.create(isbn=2, title='b', author='bjj', year=2010)
        book3 = Book.objects.create(isbn=3, title='c', author='bjj', year=2011)
        book4 = Book.objects.create(isbn=4, title='d', author='bjj', year=2011)
        book5 = Book.objects.create(isbn=5, title='e', author='x', year=2012)
        book6 = Book.objects.create(isbn=6, title='f', author='y', year=2012)

        # Create users
        user = User.objects.create(username='user',
                                   first_name='j', last_name='p', address='x', born='2023-05-11',
                                   email='user@x.com')
        user.set_password('Password1')
        user.save()

        staff = User.objects.create(username='staff',
                                    first_name='s', last_name='m', address='x', born='2023-05-11',
                                    email='staff@x.com', staff_member=True)
        staff.set_password('Password1')
        staff.save()

        # Pending request
        Loan.objects.create(book=book1, user=user)

        # Loan
        date1 = datetime.date.today()
        date2 = date1 + datetime.timedelta(28)
        Loan.objects.create(
            book=book2, user=user, loan_date=date1, return_date=date2, status='accepted', can_renew=True)

        # Loan with last day to return book
        date1 = datetime.date.today() - datetime.timedelta(28)
        date2 = datetime.date.today()
        Loan.objects.create(
            book=book3, user=user, loan_date=date1, return_date=date2, status='accepted', can_renew=True)

        # 1 day overdue loan
        date1 = datetime.date.today() - datetime.timedelta(29)
        date2 = date1 + datetime.timedelta(28)
        Loan.objects.create(
            book=book4, user=user, loan_date=date1, return_date=date2, status='accepted', can_renew=True)

        # 29 days overdue loan
        date1 = datetime.date.today() - datetime.timedelta(28 + 29)
        date2 = date1 + datetime.timedelta(28)
        Loan.objects.create(
            book=book5, user=user, loan_date=date1, return_date=date2, status='accepted', can_renew=True)

    # Test home page
    def test_unlogged_user_is_redirected_to_login_page(self):
        ''' Unlogged users should be redirected to the login page'''

        response = self.client.get(reverse('library:home'))
        return self.assertRedirects(response, reverse('users:login') + '?next=/', status_code=302, target_status_code=200)

    # Test staff member dashboard
    def test_staff_member_can_get_home_page(self):
        '''Check if staff member can get the home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(user=staff)
        response = self.client.get(reverse('library:home'))
        self.assertEqual(response.status_code, 200)

    def test_staff_member_dashboard_pending_request(self):
        '''Number of pending requests should be 1'''

        staff = User.objects.get(pk=2)
        self.client.force_login(user=staff)
        response = self.client.get(reverse('library:home'))
        return self.assertEqual(response.context.get('pending_requests').count(), 1)

    def test_staff_member_dashboard_loans(self):
        '''Number of loans should be 4'''

        staff = User.objects.get(pk=2)
        self.client.force_login(user=staff)
        response = self.client.get(reverse('library:home'))
        return self.assertEqual(response.context.get('loans').count(), 4)

    def test_staff_member_dashboard_overdue_loans(self):
        '''Number of overdue loans should be 2'''

        staff = User.objects.get(pk=2)
        self.client.force_login(user=staff)
        response = self.client.get(reverse('library:home'))
        return self.assertEqual(response.context.get('overdue_loans').count(), 2)

    def test_staff_member_dashboard_filter_users(self):
        '''Number of users which names starts with "s" should be 1'''

        staff = User.objects.get(pk=2)
        self.client.force_login(user=staff)
        data = json.dumps({'parameter': 's'})
        response = self.client.post(reverse('library:home'),
                                    data, content_type='application/json')
        return self.assertEqual(len(response.json()), 1)

    # Test user dashboard
    def test_user_can_get_home_page(self):
        '''Check if staff member can get the home page'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('library:home'))
        self.assertEqual(response.status_code, 200)

    def test_user_dashboard_borrowing(self):
        '''Number of borrowing should be 4'''

        user = User.objects.get(pk=1)
        self.client.force_login(user=user)
        response = self.client.get(reverse('library:home'))
        return self.assertEqual(response.context.get('loans').count(), 4)

    def test_user_dashboard_sorts_borrowing(self):
        '''Check if descending sort by book title works correctly'''

        user = User.objects.get(pk=1)
        self.client.force_login(user=user)
        data = json.dumps({'parameter': '-book'})
        response = self.client.post(reverse('library:home'),
                                    data, content_type='application/json')
        data = response.json().get('data')
        book_title1 = data[0].get('book_title')
        book_title2 = data[-1].get('book_title')
        self.assertEqual(book_title1, 'e')
        self.assertEqual(book_title2, 'a')

    # Test profile
    def test_user_can_get_profile_page(self):
        '''Check if user can get a profile page'''

        user = User.objects.get(pk=1)
        self.client.force_login(user=user)
        response = self.client.get(reverse('users:profile', kwargs={'pk': 2}))
        return self.assertEqual(response.status_code, 200)

    def test_unlogged_user_can_not_get_profile_page(self):
        '''Unlogged user can not get a profile page they  should be redirected to the login page'''

        response = self.client.get(reverse('users:profile', kwargs={'pk': 2}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('users:profile', kwargs={'pk': 2}), status_code=302, target_status_code=200)

    def test_profile_doesnt_exists(self):
        '''Response should return status code 404'''

        staff = User.objects.get(pk=2)
        max_pk = User.objects.aggregate(pk=Max('pk')).get('pk')
        self.client.force_login(user=staff)
        response = self.client.get(reverse('users:profile', kwargs={'pk': max_pk + 1}))
        return self.assertEqual(response.status_code, 404)

    # Test add book
    def test_get_add_book_page(self):
        '''Get the add book page should return status code 200 for staff members'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:add_book'))
        return self.assertEqual(response.status_code, 200)

    def test_get_add_book_page_forbidden(self):
        '''Get the add book page is forbidden for none staff members'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('library:add_book'))
        return self.assertEqual(response.status_code, 403)

    def test_add_book_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        response = self.client.get(reverse('library:add_book'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:add_book'),
                                    status_code=302, target_status_code=200)

    def test_add_book(self):
        ''' Add book view should redirect to the book detail page and mark the book as available '''

        staff = User.objects.get(pk=2)
        self.client.force_login(user=staff)
        response = self.client.post(reverse('library:add_book'), {
                                    'isbn': 9999999999, 'title': 'abc', 'author': 'a b', 'description': 'Lorem', 'year': 1789}, follow=True)

        queryset = Book.objects.filter(isbn=9999999999)
        self.assertEqual(queryset.count(), 1)
        book = queryset.first()
        self.assertRedirects(response, reverse('library:book_details', args=(
            book.pk,)), status_code=302, target_status_code=200)
        self.assertContains(response, f'Book is available')

    def test_add_book_isbn_exists(self):
        ''' ISBN must be a unique number. Form field error should be raised '''

        staff = User.objects.get(pk=2)
        self.client.force_login(user=staff)
        response = self.client.post(reverse('library:add_book'), {
                                    'isbn': 1, 'title': 'abc', 'author': 'a b', 'description': 'Lorem', 'year': 1789}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'isbn', [
                             'Book with this Isbn already exists.'], msg_prefix='')

    def test_add_book_isbn_is_to_long(self):
        ''' ISBN must be max 10 digits long number. Form field error should be raised '''

        staff = User.objects.get(pk=2)
        self.client.force_login(user=staff)
        response = self.client.post(reverse('library:add_book'), {
                                    'isbn': 11111111111, 'title': 'abc', 'author': 'a b', 'description': 'Lorem', 'year': 1789}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'isbn', [
                             'Ensure this value is less than or equal to 9999999999.'])

    def test_add_book_year_is_bigger_than_current_year(self):
        ''' Year cannot be bigger than current year. Form field error should be raised '''

        current_year = datetime.datetime.now().year
        staff = User.objects.get(pk=2)
        self.client.force_login(user=staff)
        response = self.client.post(reverse('library:add_book'), {
                                    'isbn': 1111111111, 'title': 'abc', 'author': 'a b', 'description': 'Lorem', 'year': current_year + 1}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'year', [
                             f'Ensure this value is less than or equal to {current_year}.'])

    # Test file add book
    def test_get_file_add_book_page(self):
        '''Get the file add book page should return status code 200 for staff members'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:file_add_book'))
        return self.assertEqual(response.status_code, 200)

    def test_get_file_add_book_page_forbidden(self):
        '''Get the file add book page is forbidden for none staff members'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('library:file_add_book'))
        return self.assertEqual(response.status_code, 403)

    def test_file_add_book_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        response = self.client.get(reverse('library:file_add_book'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:file_add_book'),
                                    status_code=302, target_status_code=200)

    def test_add_book_file(self):
        ''' Books from the file should be added. User should be redirected to the '/file/add/book/' page. Successful message should be displayed'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        with open('library/static/library/test_files/correct_data.txt') as fp:
            response = self.client.post('/file/add/book/', {'file': fp}, follow=True)
        book = Book.objects.filter(author='xxx test')
        self.assertEqual(book.count(), 2)
        self.assertContains(response, 'Books were added successfully!')
        self.assertRedirects(response, reverse('library:file_add_book'),
                             status_code=302, target_status_code=200)

    # Test get book detail
    def test_get_book_detail_page_by_unlogged_users(self):
        '''Get the book detail page should return status code 200 for unlogged users and there should not be any buttons'''

        response = self.client.get(reverse('library:book_details', kwargs={'pk': 6}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Show the add review form', status_code=200)
        self.assertNotContains(
            response, '<button id="borrowBtn" data-pk=6 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="renewBtn" data-pk=6 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)

    def test_get_book_detail_page_logged_in_users_book_available(self):
        '''Get the book detail page should return status code 200  and there should be a link to add review button, borrow button. There should not be a renew button, a delete button, an update button'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 6}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show the add review form', status_code=200, html=True)
        self.assertContains(
            response, '<button id="borrowBtn" data-pk=6 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="renewBtn" data-pk=6 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)
        self.assertContains(
            response, 'Book is available', status_code=200)

    def test_get_book_detail_page_logged_in_users_pending_request(self):
        '''Get the book detail page should return status code 200  and there should be a link to add review button, and status -pending info. There should not be a borrow button, a renew button, a delete button, an update button'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show the add review form', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="borrowBtn" data-pk=1 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="renewBtn" data-pk=1 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)
        self.assertContains(
            response, 'pending', status_code=200)

    def test_get_book_detail_page_book_borrowed_by_loggedin_user(self):
        '''Get the book detail page for lent book should return status code 200, there should be a link to add review button, and status -pending. There should be a renew button. There should not be a borrow button, a delete button, an update button'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show the add review form', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="borrowBtn" data-pk=2 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button id="renewBtn" data-pk=2 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)

    def test_get_book_detail_page_book_borrowed_by_not_loggedin_user(self):
        '''Get the book detail page for lent book should return status code 200, there should be a link to add review button, and status -pending. There should be a renew button. There should not be a renew button, a borrow button, a delete button, an update button'''

        user = User.objects.create(username='userx',
                                   first_name='j', last_name='p', address='x', born='2023-05-11',
                                   email='userx@x.com')
        user.set_password('Password1')
        user.save()
        self.client.force_login(user)
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show the add review form', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="borrowBtn" data-pk=2 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="renewBtn" data-pk=2 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)

    def test_get_book_detail_page_book_already_renewed_by_user(self):
        '''Get the book detail page for lent book should return status code 200, there should be a link to add review button, and status -pending. There should not be a renew button, a borrow button, a delete button, an update button'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)

        # Renew the book
        self.client.post(reverse('library:renew_book'),
                         {'pk': 2}, content_type='application/json')

        # Get the book page
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show the add review form', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="borrowBtn" data-pk=2 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="renewBtn" data-pk=2 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)

    def test_get_book_detail_page_logged_in_staff_book_available(self):
        '''Get the book detail page should return status code 200  and there should be a link to add review button, a borrow button a delete button, an update button. There should not be a renew button'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 6}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show the add review form', status_code=200, html=True)
        self.assertContains(
            response, '<button id="borrowBtn" data-pk=6 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="renewBtn" data-pk=6 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)
        self.assertContains(
            response, 'Book is available', status_code=200)

    def test_get_book_detail_page_logged_in_staff_pending_request(self):
        '''Get the book detail page should return status code 200  and there should be a link to add review button, and status -pending info. There should be a delete button, an update button. There should not be a borrow button, a renew button,'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show the add review form', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="borrowBtn" data-pk=1 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="renewBtn" data-pk=1 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)
        self.assertContains(
            response, 'pending', status_code=200)

    def test_get_book_detail_page_book_borrowed_by_loggedin_staff(self):
        '''Get the book detail page for lent book should return status code 200, there should be a link to add review button, and status -pending. There should be a renew button, a delete button, an update button. There should not be a borrow button'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        date1 = datetime.date.today()
        date2 = date1 + datetime.timedelta(28)
        book = Book.objects.get(pk=6)
        Loan.objects.create(
            book=book, user=staff, loan_date=date1, return_date=date2, status='accepted', can_renew=True)
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 6}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show the add review form', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="borrowBtn" data-pk=6 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button id="renewBtn" data-pk=6 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)

    def test_get_book_detail_page_book_borrowed_by_not_loggedin_user(self):
        '''Get the book detail page for lent book should return status code 200, there should be a link to add review button, and status -pending. There should be a renew button, a delete button, an update button. There should not be a renew button, a borrow button'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show the add review form', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="borrowBtn" data-pk=2 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="renewBtn" data-pk=2 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)

    def test_get_book_detail_page_book_already_renewed_by_staff(self):
        '''Get the book detail page for lent book should return status code 200, there should be a link to add review button, and status -pending. There should not be a renew button, a borrow button. There should be a delete button, an update button'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        date1 = datetime.date.today()
        date2 = date1 + datetime.timedelta(28)
        book = Book.objects.get(pk=6)
        Loan.objects.create(
            book=book, user=staff, loan_date=date1, return_date=date2, status='accepted', can_renew=True)

        # Renew the book
        self.client.post(reverse('library:renew_book'),
                         {'pk': 6}, content_type='application/json')

        # Get the book page
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 6}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show the add review form', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="borrowBtn" data-pk=6 class="btn btn-outline-success">Borrow</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button id="renewBtn" data-pk=6 class="btn btn-outline-dark">Renew</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)

    def test_get_none_existing_book_page(self):
        '''Getting none existing book page should raise 404'''

        response = self.client.get(reverse('library:book_details', kwargs={'pk': 10000}))
        self.assertEqual(response.status_code, 404)

    # Test book deletion
    def test_get_delete_book_displays_confirm_deletion(self):
        '''delete_book get request asks for confirmation'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.first()
        response = self.client.get(reverse('library:book_delete', kwargs={'pk': book.pk}))
        return self.assertContains(
            response, f'Do you really want to delete the book')

    def test_staff_member_can_delete_book(self):
        '''Staff member should be able to remove book and should be redirected to home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=6)
        response = self.client.post(
            reverse('library:book_delete', kwargs={'pk': book.pk}), follow=True)
        queryset = Book.objects.filter(pk=book.pk)
        self.assertEqual(queryset.count(), 0)
        self.assertRedirects(response, reverse('library:home'),
                             status_code=302, target_status_code=200)

    def test_user_cannot_delete_book(self):
        '''Removing books is forbidden for none staff members '''

        user = User.objects.get(pk=1)
        book = Book.objects.get(pk=6)
        self.client.force_login(user)
        response = self.client.post(
            reverse('library:book_delete', kwargs={'pk': book.pk}), follow=True)
        queryset = Book.objects.filter(pk=book.pk)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(response.status_code, 403)

    def test_book_can_not_be_deleted(self):
        '''Lent book can not be deleted'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=1)
        response = self.client.post(
            reverse('library:book_delete', kwargs={'pk': book.pk}), follow=True)
        queryset = Book.objects.filter(pk=book.pk)
        self.assertEqual(queryset.count(), 1)
        self.assertRedirects(response, reverse('library:book_details', kwargs={'pk': book.pk}),
                             status_code=302, target_status_code=200)
        self.assertContains(
            response, f'You can not delete a lent book.')

    def test_delete_book_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        book = Book.objects.get(pk=6)
        response = self.client.get(
            reverse('library:book_delete', kwargs={'pk': book.pk}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:book_delete', kwargs={'pk': book.pk}),
                                    status_code=302, target_status_code=200)

    def test_delete_book_book_doesnt_exists(self):
        '''Response should return status code 404'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.post(
            reverse('library:book_delete', kwargs={'pk': 10000000}), follow=True)
        self.assertEqual(response.status_code, 404)

    # Test book update
    def test_get_book_update_page(self):
        '''Get book update page should return status code 200'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:book_details', kwargs={'pk': 1}))
        return self.assertEqual(response.status_code, 200)

    def test_staff_member_can_update_book(self):
        '''Staff member should be able to update book and should be redirected to the book page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.post(reverse('library:book_update', kwargs={'pk': 1}), {
                                    'isbn': 1, 'title': 'Test update', 'author': 'a b', 'description': 'Lorem', 'year': 1789}, follow=True)
        book = Book.objects.get(isbn=1)
        self.assertEqual(book.title, 'Test update')
        self.assertRedirects(response, reverse('library:book_details', kwargs={'pk': book.pk}),
                             status_code=302, target_status_code=200)

    def test_user_cannot_update_book(self):
        '''Updating books is forbidden for none staff members '''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(
            reverse('library:book_update', kwargs={'pk': user.pk}), follow=True)
        return self.assertEqual(response.status_code, 403)

    def test_update_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        response = self.client.get(reverse('library:book_update', kwargs={'pk': 1}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:book_update', kwargs={'pk': 1}),
                                    status_code=302, target_status_code=200)

    def test_update_book_book_doesnt_exists(self):
        '''Response should return status code 404'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.post(reverse('library:book_update', kwargs={'pk': 10000000}), {
                                    'isbn': 1, 'title': 'Test update', 'author': 'a b', 'description': 'Lorem', 'year': 1789}, follow=True)
        self.assertEqual(response.status_code, 404)

    # Borrow book
    def test_get_borrow_book_logged_users(self):
        '''Get method is not allowed should redirect user to the home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:borrow_book'), follow=True)
        self.assertRedirects(response, reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(response, 'Wrong request.')

    def test_get_return_book_unlogged_users(self):
        '''Get method is not allowed should redirect user to the login page'''

        response = self.client.get(reverse('library:borrow_book'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:borrow_book'),
                                    status_code=302, target_status_code=200)

    def test_borrow_book(self):
        ''' User and staff member can borrow book and they should be redirected to the book page.'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=6)
        response = self.client.post(reverse('library:borrow_book'),
                                    {'pk': book.pk}, content_type='application/json')
        loan_query = Loan.objects.filter(book=book)
        self.assertEqual(loan_query.count(), 1)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('message'),
                         f'You have requested "{book.title}" by {book.author}. Your request is waiting for approval.')
        self.assertEqual(data.get('flag'), 'ok')
        self.assertEqual(data.get('loan_pk'), loan_query.get().pk)

    def test_borrow_book_not_available(self):
        '''If book is not available user should redirected to the home page and error message should be displayed '''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=1)
        response = self.client.post(reverse('library:borrow_book'),
                                    {'pk': book.pk},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('message'),
                         f'The book "{book.title}" by {book.author} is not available.')

    def test_borrow_book_user_has_more_than_10_book(self):
        '''If user has borrowed more than 10 books error message should be returned'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        for i in range(7, 13):
            book = Book.objects.create(isbn=i, title='f', author='f', year=2012)
            Loan.objects.create(book=book, user=user)
        response = self.client.post(reverse('library:borrow_book'),
                                    {'pk': 6},
                                    content_type='application/json')
        data = response.json()
        self.assertEqual(data.get('message'),
                         f'User "{user}" has already borrowed the maximum number of books.')

    def test_borrow_book_book_doesnt_exists(self):
        ''' Response should return status code 404'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.post(reverse('library:borrow_book'),
                                    {'pk': 1000000}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    # Test loan
    def test_loan_date_pending_request(self):
        '''Loan date does not exists if request is pending'''

        loan = Loan.objects.get(pk=1)
        return self.assertEqual(loan.loan_date, None)

    def test_return_date_pending_request(self):
        '''Return date does not exists if request is pending'''

        loan = Loan.objects.get(pk=1)
        return self.assertEqual(loan.return_date, None)

    def test_loan_is_not_overdue(self):
        '''Check if loan is not overdue'''

        loan = Loan.objects.get(pk=2)
        return self.assertFalse(loan.is_overdue)

    def test_last_day_return_loan_is_not_overdue(self):
        '''Check if loan with last day return day is not overdue'''

        loan = Loan.objects.get(pk=3)
        return self.assertFalse(loan.is_overdue)

    def test_loan_fee_zero(self):
        '''Fee for not overdue loan should be 0'''

        loan = Loan.objects.get(pk=2)
        return self.assertEqual(loan.fee, 0)

    def test_loan_overdue(self):
        '''Check if loan is overdue'''

        loan = Loan.objects.get(pk=4)
        return self.assertTrue(loan.is_overdue)

    def test_loan_fee_greater_zero(self):
        '''Check if loan fee is greater than zero for overdue loan'''

        loan = Loan.objects.get(pk=4)
        return self.assertNotEqual(loan.fee, 0)

    def test_loan_fee_30(self):
        '''Fee for 29 days overdue loan should be 30'''

        loan = Loan.objects.get(pk=5)
        return self.assertEqual(loan.fee, 30)

    # Test get loan details
    def test_get_request_detail_page_logged_in_user(self):
        '''Get the request detail page by none staff members should return status code 200  and there should not be update button, delete button, accept button, reject request button'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('library:loan_details', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertNotContains(
            response, f'<button id="acceptBtn" data-bookpk="1" class="btn btn-outline-success">Accept</button>', status_code=200, html=True)
        self.assertNotContains(
            response, f'<button id="rejectBtn" data-bookpk="1" class="btn btn-outline-warning">Reject request</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<input id="returnBtn" class="btn btn-outline-dark" type="submit" name="" value="Return book">', status_code=200, html=True)

    def test_get_request_detail_page_logged_in_staff(self):
        '''Get the request detail page by staff members should return status code 200 and there should be update button, delete button, accept button, reject request button and there should not be return button'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        response = self.client.get(reverse('library:loan_details', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertContains(
            response, f'<button id="acceptBtn" data-bookpk="1" class="btn btn-outline-success">Accept</button>', status_code=200, html=True)
        self.assertContains(
            response, f'<button id="rejectBtn" data-bookpk="1" class="btn btn-outline-warning">Reject request</button>', status_code=200, html=True)
        self.assertNotContains(
            response, '<input id="returnBtn" class="btn btn-outline-dark" type="submit" name="" value="Return book">', status_code=200, html=True)

    def test_get_loan_detail_page_logged_in_staff(self):
        '''Get the request detail page by staff members should return status code 200 and there should be update button, delete button, return buttton and should not be accept button, reject request button'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        response = self.client.get(reverse('library:loan_details', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<button class="btn btn-outline-info">Update</button>', status_code=200, html=True)
        self.assertContains(
            response, '<button class="btn btn-outline-danger">Delete</button>', status_code=200, html=True)
        self.assertContains(
            response, '<input id="returnBtn" class="btn btn-outline-dark" type="submit" name="" value="Return book">', status_code=200, html=True)
        self.assertNotContains(
            response, f'<button id="acceptBtn" data-bookpk="2" class="btn btn-outline-success">Accept</button>', status_code=200, html=True)
        self.assertNotContains(
            response, f'<button id="rejectBtn" data-bookpk="2" class="btn btn-outline-warning">Reject request</button>', status_code=200, html=True)

    def test_get_request_detail_page_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        response = self.client.get(reverse('library:loan_details', kwargs={'pk': 1}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:loan_details', kwargs={'pk': 1}),
                                    status_code=302, target_status_code=200)

    def test_get_none_existing_loan_page(self):
        '''Getting none existing loan page should raise 404'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        response = self.client.get(reverse('library:loan_details', kwargs={'pk': 10000}))
        return self.assertEqual(response.status_code, 404)

    # Test loan deletion
    def test_get_delete_loan_displays_confirm_deletion(self):
        '''Get loan delete asks for confirmation'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        loan = Loan.objects.first()
        response = self.client.get(reverse('library:loan_delete', kwargs={'pk': loan.pk}))
        return self.assertContains(
            response, f'Do you really want to delete the request')

    def test_staff_member_can_delete_loan(self):
        '''Staff member should be able to remove loan and should be redirected to user\'s profile'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        loan = Loan.objects.get(pk=2)
        response = self.client.post(
            reverse('library:loan_delete', kwargs={'pk': loan.pk}), follow=True)
        queryset = Loan.objects.filter(pk=loan.pk)
        self.assertEqual(queryset.count(), 0)
        self.assertRedirects(response, reverse('users:profile', kwargs={'pk': loan.user.pk}),
                             status_code=302, target_status_code=200)

    def test_user_cannot_delete_book(self):
        '''Removing loans is forbidden for none staff members '''

        user = User.objects.get(pk=1)
        loan = Loan.objects.get(pk=2)
        self.client.force_login(user)
        response = self.client.post(
            reverse('library:loan_delete', kwargs={'pk': loan.pk}), follow=True)
        queryset = Book.objects.filter(pk=loan.pk)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(response.status_code, 403)

    def test_delete_loan_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        loan = Loan.objects.get(pk=2)
        response = self.client.get(
            reverse('library:loan_delete', kwargs={'pk': loan.pk}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:loan_delete', kwargs={'pk': loan.pk}),
                                    status_code=302, target_status_code=200)

    def test_loan_delete_page_loan_doesnt_exists(self):
        '''Response should return status code 404'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.post(
            reverse('library:loan_delete', kwargs={'pk': 1000}), follow=True)
        return self.assertEqual(response.status_code, 404)

    # Test loan update
    def test_get_loan_update_page(self):
        '''Get loan update page should return status code 200'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        loan = Loan.objects.get(pk=1)
        response = self.client.get(reverse('library:loan_details', kwargs={'pk': loan.pk}))
        return self.assertEqual(response.status_code, 200)

    def test_get_loan_update_page_loan_doesnt_exists(self):
        '''Response should return status code 404'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:loan_details', kwargs={'pk': 100}))
        return self.assertEqual(response.status_code, 404)

    def test_staff_member_can_update_loan(self):
        '''Staff member should be able to update loan and should be redirected to the loan page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        loan = Loan.objects.get(pk=1)
        response = self.client.post(reverse('library:loan_update', kwargs={'pk': loan.pk}), {
                                    'book': '1', 'user': '2', 'loan_date': '2023-05-28', 'return_date': '2023-07-25', 'status': 'accepted', 'can_renew': 'on'})
        loan = Loan.objects.get(pk=loan.pk)
        self.assertEqual(loan.return_date, datetime.date(2023, 7, 25))
        self.assertRedirects(response, reverse('library:loan_details', kwargs={'pk': loan.pk}),
                             status_code=302, target_status_code=200)

    def test_loan_date_greater_than_return_date(self):
        '''Form error should be raised if loan date is greather than return date'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        loan = Loan.objects.get(pk=1)
        response = self.client.post(reverse('library:loan_update', kwargs={'pk': loan.pk}), {
                                    'book': '1', 'user': '2', 'loan_date': '2023-05-25', 'return_date': '2023-04-25', 'status': 'accepted', 'can_renew': 'on'})
        return self.assertFormError(response, 'form', 'return_date',
                                    'Loan date can not be greater than return date.')

    def test_loan_date_greater_than_return_date(self):
        '''Form error should be raised if loan date is greather than return date'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        loan = Loan.objects.get(pk=1)
        response = self.client.post(reverse('library:loan_update', kwargs={'pk': loan.pk}), {
                                    'book': '1', 'user': '2', 'loan_date': '2023-05-25', 'return_date': '2023-04-25', 'status': 'accepted', 'can_renew': 'on'})
        return self.assertFormError(response, 'form', 'return_date',
                                    'Loan date can not be greater than return date.')

    def test_loan_status_accepted_loan_date_none(self):
        '''Form error should be raised if loan status is accepted and loan date is none'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        loan = Loan.objects.get(pk=1)
        response = self.client.post(reverse('library:loan_update', kwargs={'pk': loan.pk}), {
                                    'book': '1', 'user': '2', 'loan_date': '', 'return_date': '2023-04-25', 'status': 'accepted', 'can_renew': 'on'})
        return self.assertFormError(response, 'form', 'loan_date',
                                    'Accepted loan must have loan date.')

    def test_loan_status_accepted_return_date_none(self):
        '''Form error should be raised if loan status is accepted and return date is none'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        loan = Loan.objects.get(pk=1)
        response = self.client.post(reverse('library:loan_update', kwargs={'pk': loan.pk}), {
                                    'book': '1', 'user': '2', 'loan_date': '2023-04-25', 'return_date': '', 'status': 'accepted', 'can_renew': 'on'})
        return self.assertFormError(response, 'form', 'return_date',
                                    'Accepted loan must have return date.')

    def test_loan_wrong_date_format(self):
        '''Form error should be raised if date format is wrong'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        loan = Loan.objects.get(pk=1)
        response = self.client.post(reverse('library:loan_update', kwargs={'pk': loan.pk}), {
                                    'book': '1', 'user': '2', 'loan_date': '2023-10-10', 'return_date': '2023/10/20', 'status': 'accepted', 'can_renew': 'on'})
        return self.assertFormError(response, 'form', 'return_date',
                                    'Enter a valid date.')

    def test_user_cannot_update_loan(self):
        '''Updating loans is forbidden for none staff members '''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(
            reverse('library:loan_update', kwargs={'pk': user.pk}), follow=True)
        return self.assertEqual(response.status_code, 403)

    def test_update_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        response = self.client.get(reverse('library:loan_update', kwargs={'pk': 1}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:loan_update', kwargs={'pk': 1}),
                                    status_code=302, target_status_code=200)

    # Test accept request
    def test_get_accept_request_page_logged_users(self):
        '''Get method is not allowed should redirect user to the home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:accept_request'), follow=True)
        self.assertRedirects(response, reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(response, 'Wrong request.')

    def test_get_accept_request_page_unlogged_users(self):
        '''Get method is not allowed should redirect user to the login page'''

        response = self.client.get(reverse('library:accept_request'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:accept_request'),
                                    status_code=302, target_status_code=200)

    def test_accept_request(self):
        ''' Staff member can accept request.'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=1)
        response = self.client.post(reverse('library:accept_request'),
                                    json.dumps({"bookpk": str(book.pk)}), content_type='application/json')
        loan = Loan.objects.get(book=book)
        self.assertEqual(loan.status, 'accepted')
        data = response.json()
        message = data.get('message')
        self.assertEqual(
            message, f'Request for "{book.title}" by {book.author} by the user "{loan.user}" has been accepted.')
        flag = message = data.get('flag')
        self.assertEqual(flag, 'OK')
        owner_pk = data.get('owner_pk')
        self.assertEqual(owner_pk, loan.user.pk)
        owner = data.get('owner')
        self.assertEqual(owner, loan.user.username)
        loan_date = data.get('loan_date')
        self.assertEqual(loan_date, loan.loan_date.strftime('%Y-%m-%d'))
        return_date = data.get('return_date')
        self.assertEqual(return_date, loan.return_date.strftime('%Y-%m-%d'))

    def test_accept_request_by_none_staff_members(self):
        ''' Accepting requests for none staff members is forbidden they should be redirected to the login page. '''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        book = Book.objects.get(pk=1)
        response = self.client.post(reverse('library:accept_request'),
                                    json.dumps({"bookpk": str(book.pk)}), content_type='application/json', follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:accept_request'),
                                    status_code=302, target_status_code=200)

    def test_no_pending_request(self):
        '''No pending request should return error message'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=3)
        response = self.client.post(reverse('library:accept_request'),
                                    json.dumps({"bookpk": str(book.pk)}), content_type='application/json')
        message = response.json().get('message')
        return self.assertEqual(
            message, f'There is no pending request for "{book.title}" by {book.author}.')

    def test_no_request(self):
        '''No request should return error message'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.create(isbn=60, title='f', author='f', year=2012)
        response = self.client.post(reverse('library:accept_request'),
                                    json.dumps({'bookpk': book.pk}), content_type='application/json')
        message = response.json().get('message')
        return self.assertEqual(
            message, f'There is no such request for "{book.title}" by {book.author}.')

    # Test reject request
    def test_get_reject_request_page_logged_users(self):
        '''Get method is not allowed should redirect user to the home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:reject_request'), follow=True)
        self.assertRedirects(response, reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(response, 'Wrong request.')

    def test_get_reject_request_page_unlogged_users(self):
        '''Get method is not allowed should redirect user to the login page'''

        response = self.client.get(reverse('library:reject_request'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:reject_request'),
                                    status_code=302, target_status_code=200)

    def test_reject_request_with_reject_message(self):
        ''' Staff member can reject request. History object should be created. User should be redirected to the book page.'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=1)
        request = Loan.objects.get(book=book)
        response = self.client.post(reverse('library:reject_request'),
                                    {'bookpk': book.pk, 'rejectMessage': 'My reject message'}, follow=True)
        queryset = History.objects.filter(book=book)
        self.assertEqual(queryset.count(), 1)
        history_obj = queryset.get()
        self.assertEqual(history_obj.loan_date, None)
        self.assertEqual(history_obj.reject_message, '"My reject message"')
        self.assertEqual(history_obj.loan_date, None)
        self.assertEqual(history_obj.return_date, None)
        self.assertEqual(history_obj.book, book)
        self.assertEqual(history_obj.user, request.user)
        self.assertEqual(history_obj.status, 'rejected')
        self.assertRedirects(response, reverse('library:book_details', kwargs={'pk': book.pk}),
                             status_code=302, target_status_code=200)
        self.assertContains(
            response, f'The request for the book &quot;{book.title}&quot; by the user &quot;{request.user.username}&quot; has been rejected.')

    def test_reject_request_without_reject_message(self):
        ''' Staff member can reject request without reject message. History object should be created. User should be redirected to the book page.'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=1)
        request = Loan.objects.get(book=book)
        response = self.client.post(reverse('library:reject_request'),
                                    {'bookpk': book.pk, 'rejectMessage': ''}, follow=True)
        queryset = History.objects.filter(book=book)
        self.assertEqual(queryset.count(), 1)
        history_obj = queryset.get()
        self.assertEqual(history_obj.loan_date, None)
        self.assertEqual(history_obj.reject_message, '""')
        self.assertEqual(history_obj.loan_date, None)
        self.assertEqual(history_obj.return_date, None)
        self.assertEqual(history_obj.book, book)
        self.assertEqual(history_obj.user, request.user)
        self.assertEqual(history_obj.status, 'rejected')
        self.assertRedirects(response, reverse('library:book_details', kwargs={'pk': book.pk}),
                             status_code=302, target_status_code=200)
        self.assertContains(
            response, f'The request for the book &quot;{book.title}&quot; by the user &quot;{request.user.username}&quot; has been rejected.')

    def test_reject_request_by_none_staff_members(self):
        ''' Rejecting requests for none staff members is forbidden they should be redirected to the login page. '''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        book = Book.objects.get(pk=1)
        response = self.client.post(reverse('library:reject_request'),
                                    {'bookpk': book.pk, 'rejectMessage': 'My reject message'}, follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:reject_request'),
                                    status_code=302, target_status_code=200)

    def test_reject_request_no_pending_request(self):
        '''No pending request should redirect to the home page and display error message'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=3)
        loan = Loan.objects.get(book=book)
        response = self.client.post(reverse('library:reject_request'),
                                    {'bookpk': book.pk, 'rejectMessage': 'My reject message'}, follow=True)
        self.assertRedirects(response,  reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(
            response, f'There is no pending request for &quot;{book.title}&quot; by {book.author}.')

    def test_reject_request_no_request(self):
        '''No request should redirect to the home page and display error message'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.create(isbn=60, title='f', author='f', year=2012)
        response = self.client.post(reverse('library:reject_request'),
                                    {'bookpk': book.pk, 'rejectMessage': 'My reject message'}, follow=True)
        self.assertRedirects(response,  reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(
            response, f'There is no such request for &quot;{book.title}&quot; by {book.author}.')

    # Test return book
    def test_get_return_book_logged_users(self):
        '''Get method is not allowed should redirect user to the home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:return_book'), follow=True)
        self.assertRedirects(response, reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(response, 'Wrong request.')

    def test_get_return_book_unlogged_users(self):
        '''Get method is not allowed should redirect user to the login page'''

        response = self.client.get(reverse('library:return_book'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:return_book'),
                                    status_code=302, target_status_code=200)

    def test_return_book(self):
        ''' Staff member can return book. User should be redirected to the book page.'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=2)
        request = Loan.objects.get(book=book)
        response = self.client.post(reverse('library:return_book'),
                                    {'bookpk': book.pk}, follow=True)
        self.assertRedirects(response, reverse('library:book_details', kwargs={'pk': book.pk}),
                             status_code=302, target_status_code=200)
        self.assertContains(
            response, f'The book &quot;{book.title}&quot; by {book.author} has been returned.')

    def test_return_book_by_none_staff_members(self):
        ''' Return books for none staff members is forbidden they should be redirected to the login page. '''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        book = Book.objects.get(pk=1)
        response = self.client.post(reverse('library:return_book'),
                                    {'bookpk': book.pk}, follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:return_book'),
                                    status_code=302, target_status_code=200)

    def test_return_book_no_loan(self):
        '''No loan should redirect to the home page and display error message'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=6)
        response = self.client.post(reverse('library:return_book'),
                                    {'bookpk': book.pk}, follow=True)
        self.assertRedirects(response,  reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(
            response, f'There is no such request for &quot;{book.title}&quot; by {book.author}.')

    def test_return_book_no_accepted_request(self):
        '''No acccepted request should redirect user to the home page and display error message'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=1)
        response = self.client.post(reverse('library:return_book'),
                                    {'bookpk': book.pk}, follow=True)
        self.assertRedirects(response,  reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(
            response, f'The request has not been accepted.')

    def test_return_book_book_doesnt_exists(self):
        '''Response code status should be 404'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        pk = Book.objects.aggregate(pk=Max('pk')).get('pk') + 1
        response = self.client.post(reverse('library:return_book'),
                                    {'bookpk': pk}, follow=True)

    # Renew book
    def test_get_renew_book_logged_users(self):
        '''Get method is not allowed should redirect user to the home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:renew_book'), follow=True)
        self.assertRedirects(response, reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(response, 'Wrong request.')

    def test_get_renew_book_unlogged_users(self):
        '''Get method is not allowed should redirect user to the login page'''

        response = self.client.get(reverse('library:renew_book'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:renew_book'),
                                    status_code=302, target_status_code=200)

    def test_renew_book(self):
        ''' User can renew book. Return date should be extented for 14 days, and can renew attribute should be change to false'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        book = Book.objects.get(pk=2)
        loan = Loan.objects.get(book=book)
        response = self.client.post(reverse('library:renew_book'),
                                    {'pk': book.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        renewed_loan = Loan.objects.get(book=book)
        self.assertFalse(renewed_loan.can_renew)
        data = response.json()
        self.assertEqual(data.get('message'),
                         f'The book \"{book.title}\" by {book.author} has been renewed.')
        self.assertEqual(data.get('return_date'), (loan.return_date + datetime.timedelta(14)).strftime(
            '%Y-%m-%d'))

    def test_renew_book_already_renewed(self):
        '''If book has been already renewed and error message should be returned'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        book = Book.objects.get(pk=2)
        loan = Loan.objects.get(book=book)
        loan.can_renew = False
        loan.save()
        response = self.client.post(reverse('library:renew_book'),
                                    {'pk': book.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('message'),
                         f'You can not renew the book "{book.title}" by {book.author} twice. It has been already renewed.')

    def test_renew_book_by_not_book_owner(self):
        '''Renew book can only users who borrowed the book'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=2)
        loan = Loan.objects.get(book=book)
        response = self.client.post(reverse('library:renew_book'),
                                    {'pk': book.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('message'),
                         f'You are not allowed to renew the book "{book.title}" by {book.author}.')

    def test_renew_book_no_loan(self):
        '''No loan should should return error message'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=6)
        response = self.client.post(reverse('library:renew_book'),
                                    {'pk': book.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('message'),
                         f'There is no such request for "{book.title}" by {book.author} and user {staff}.')

    def test_renew_book_no_accepted_request(self):
        '''No acccepted request should return error message'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=1)
        response = self.client.post(reverse('library:renew_book'),
                                    {'pk': book.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('message'),
                         f'There is no such accepted request for "{book.title}" by {book.author} and user {staff}.')

    def test_renew_book_book_doesnt_exists(self):
        '''Response code status should be 404'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(reverse('library:renew_book'),
                                    {'pk': 1000000}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    # Add book review
    def test_add_review_logged_users(self):
        '''Get method is not allowed should redirect user to the home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:add_review'), follow=True)
        self.assertRedirects(response, reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(response, 'Wrong request.')

    def test_get_add_review_unlogged_users(self):
        '''Get method is not allowed should redirect user to the login page'''

        response = self.client.get(reverse('library:add_review'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:add_review'),
                                    status_code=302, target_status_code=200)

    def test_add_review(self):
        ''' User can review a book'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        book = Book.objects.get(pk=1)
        response = self.client.post(reverse('library:add_review'),
                                    {'bookPk': book.pk, 'content': 'My review'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        max_pk = Book_Review.objects.all().count()
        review_query = Book_Review.objects.filter(pk=max_pk)
        self.assertEqual(review_query.count(), 1)
        data = response.json()
        self.assertEqual(data.get('id'), max_pk)
        self.assertEqual(data.get('book_id'), book.id)
        self.assertEqual(data.get('author_id'), user.pk)
        self.assertEqual(data.get('content'), 'My review')
        self.assertTrue(data.get('creation_date'))
        self.assertEqual(data.get('author__username'), user.username)

    def test_add_review_book_doesnt_exists(self):
        ''' Response code status should be 404'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(reverse('library:add_review'),
                                    {'bookPk': 1000000, 'content': 'My review'}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    # Load reviews
    def test_load_reviews(self):
        ''' Users can get book reviews'''

        user = User.objects.get(pk=1)
        book = Book.objects.get(pk=1)
        for i in range(3):
            review = Book_Review(book=book, author=user, content='Content')
            review.save()
        response = self.client.get(reverse('library:load_reviews', kwargs={'pk': book.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 3)
        self.assertIn('author_id', data[0])
        self.assertIn('author__username', data[0])
        self.assertIn('creation_date', data[0])
        self.assertIn('id', data[0])
        self.assertIn('content', data[0])

    def test_load_reviews_book_doesnt_exists(self):
        ''' Response code status should be 404'''

        user = User.objects.get(pk=1)
        response = self.client.get(reverse('library:load_reviews', kwargs={'pk': 100000}))
        self.assertEqual(response.status_code, 404)

    # Edit review
    def test_edit_review_logged_users(self):
        '''Get method is not allowed should redirect user to the home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:edit_review'), follow=True)
        self.assertRedirects(response, reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(response, 'Wrong request.')

    def test_edit_review_unlogged_users(self):
        '''Get method is not allowed should redirect user to the login page'''

        response = self.client.get(reverse('library:edit_review'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:edit_review'),
                                    status_code=302, target_status_code=200)

    def test_edit_review(self):
        ''' Review author can edit his own review'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        book = Book.objects.get(pk=1)
        review = Book_Review(book=book, author=user, content='My review')
        review.save()
        response = self.client.post(reverse('library:edit_review'),
                                    {'author_id': user.pk, 'content': 'Content changed', 'id': review.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        review_query = Book_Review.objects.filter(pk=review.pk)
        self.assertEqual(review_query.count(), 1)
        data = response.json()
        self.assertEqual(data.get('id'), review.pk)
        self.assertEqual(data.get('author_id'), user.pk)
        self.assertEqual(data.get('content'), 'Content changed')
        self.assertTrue(data.get('creation_date'))
        self.assertEqual(data.get('author__username'), user.username)

    def test_edit_review_by_not_review_author(self):
        '''Only author can edit review'''

        user = User.objects.get(pk=1)
        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=1)
        review = Book_Review(book=book, author=user, content='My review')
        review.save()
        response = self.client.post(reverse('library:edit_review'),
                                    {'author_id': user.pk, 'content': 'Content changed', 'id': review.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_edit_review_review_doesnt_exists(self):
        '''Response should return status code 404'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        book = Book.objects.get(pk=1)
        response = self.client.post(reverse('library:edit_review'),
                                    {'author_id': user.pk, 'content': 'Content changed', 'id': 100}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    # Delete review
    def test_delete_review_logged_users(self):
        '''Get method is not allowed should redirect user to the home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:del_review'), follow=True)
        self.assertRedirects(response, reverse('library:home'),
                             status_code=302, target_status_code=200)
        self.assertContains(response, 'Wrong request.')

    def test_delete_review_unlogged_users(self):
        '''Get method is not allowed should redirect user to the login page'''

        response = self.client.get(reverse('library:del_review'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:del_review'),
                                    status_code=302, target_status_code=200)

    def test_delete_review(self):
        ''' Review author can delete his own review'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        book = Book.objects.get(pk=1)
        review = Book_Review(book=book, author=user, content='My review')
        review.save()
        response = self.client.post(reverse('library:del_review'),
                                    {'author_id': user.pk, 'content': 'Content changed', 'id': review.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        review_query = Book_Review.objects.filter(pk=review.pk)
        self.assertEqual(review_query.count(), 0)
        data = response.json()
        self.assertEqual(data.get('id'), review.pk)

    def test_delete_review_by_not_review_author(self):
        '''Only author can delete review'''

        user = User.objects.get(pk=1)
        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        book = Book.objects.get(pk=1)
        review = Book_Review(book=book, author=user, content='My review')
        review.save()
        response = self.client.post(reverse('library:del_review'),
                                    {'author_id': user.pk, 'id': review.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_delete_review_review_doesnt_exists(self):
        '''Response should return status code 404'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        book = Book.objects.get(pk=1)
        response = self.client.post(reverse('library:del_review'),
                                    {'author_id': user.pk, 'content': 'Content changed', 'id': 100}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    # Test history
    def test_history(self):
        '''Check if history object is created after loan deletion'''

        loan = Loan.objects.get(pk=4)
        loan.delete()
        c = History.objects.all().count()
        return self.assertEqual(c, 1)

    def test_history_details(self):
        '''All users can get history details'''

        loan = Loan.objects.get(pk=4)
        loan.delete()
        pk = History.objects.aggregate(pk=Max('pk')).get('pk')
        response = self.client.get(reverse('library:history_details', kwargs={'pk': pk}))
        return self.assertEqual(response.status_code, 200)

    def test_history_details_page_doesnt_exists(self):
        '''Response should return status code 404'''

        response = self.client.get(reverse('library:history_details', kwargs={'pk': 1000}))
        return self.assertEqual(response.status_code, 404)

    # Test user reviews
    def test_user_reviews_unlogged_users(self):
        '''Unlogged users should be redirected to the login page'''

        response = self.client.get(reverse('library:user_reviews', kwargs={'pk': 1}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('library:user_reviews', kwargs={'pk': 1}),
                                    status_code=302, target_status_code=200)

    def test_user_reviews(self):
        '''Get user reviews should return all users\' reviews plus users instance '''

        book = Book.objects.get(pk=1)
        user = User.objects.get(pk=1)
        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        for i in range(3):
            review = Book_Review(book=book, author=user, content='Content')
            review.save()
        response = self.client.get(reverse('library:user_reviews', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('object_list').count(), 3)
        self.assertIn('author', response.context)
        self.assertTrue(response.context.get('author'), user)

    def test_user_reviews_user_doesnt_exists(self):
        '''Response should return status code 404'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('library:user_reviews', kwargs={'pk': 1000000}))
        self.assertEqual(response.status_code, 404)

    # Test search books
    def test_search_get_page(self):
        '''Get search link should, return info message'''

        response = self.client.get(reverse('library:search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a query to get results.')

    def test_search_for_book_title(self):
        '''Search for title "f", should return 1 book,
        search for title "bjj", should return 3 books'''

        response = self.client.get('/search/?q=f')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('page_obj').paginator.count, 1)

    def test_search_for_author(self):
        '''Search for title "bjj", should return 3 books'''

        response = self.client.get('/search/?q=bjj')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('page_obj').paginator.count, 3)

    def test_search_no_query(self):
        '''Search without query, should return all books'''

        response = self.client.get('/search/?q=')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('page_obj').paginator.count, 6)

    def test_search_no_results(self):
        ''' If there there are no results, message should be returned'''

        query = 'xxxx'
        response = self.client.get(reverse('library:search') + f'?q={query}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'There are no results for &quot;{query}&quot;.')


if __name__ == '__main__':
    TestCase.main()
