from django.test import TestCase
from library.models import Loan, Book, History
from .models import User
import datetime
from django.test import Client, override_settings
from django.urls import reverse
from django.db.models import Avg, Max, Min, Sum, Count
import json
from django.test import tag
import os
from final_project.settings import MEDIA_URL


class LibraryTestCase(TestCase):
    def setUp(self):
        # Create client object as attribute
        self.client = Client()

        # Create books
        book1 = Book.objects.create(isbn=1, title='a', author='bj', year=2000)
        book2 = Book.objects.create(isbn=2, title='b', author='bjj', year=2010)
        book3 = Book.objects.create(isbn=3, title='c', author='bjj', year=2011)
        book4 = Book.objects.create(isbn=4, title='d', author='bjj', year=2011)
        book5 = Book.objects.create(isbn=5, title='e', author='a', year=2012)

        # Create users
        user = User.objects.create(username='user',
                                   first_name='j', last_name='p', address='x', born='2023-05-11',
                                   email='user@x.com', staff_member=False)
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
            book=book2, user=user, loan_date=date1, return_date=date2, status='accepted')

        # Loan with last day to return book
        date1 = datetime.date.today() - datetime.timedelta(28)
        date2 = datetime.date.today()
        Loan.objects.create(
            book=book3, user=user, loan_date=date1, return_date=date2, status='accepted')

        # 1 day overdue loan
        date1 = datetime.date.today() - datetime.timedelta(29)
        date2 = date1 + datetime.timedelta(28)
        Loan.objects.create(
            book=book4, user=user, loan_date=date1, return_date=date2, status='accepted')

        # 29 days overdue loan
        date1 = datetime.date.today() - datetime.timedelta(28 + 29)
        date2 = date1 + datetime.timedelta(28)
        Loan.objects.create(
            book=book5, user=user, loan_date=date1, return_date=date2, status='accepted')

    # Test login
    def test_user_can_login(self):
        '''Check if user can login'''

        response = self.client.login(username='user', password='Password1')
        return self.assertTrue(response)

    def test_user_can_not_login(self):
        '''Check if user can not login by typing wrong password'''

        response = self.client.login(username='user', password='Password2')
        return self.assertFalse(response)

    def test_get_login_page(self):
        ''' Code status should be 200 for getting the loading page'''

        response = self.client.get(reverse('users:login'))
        return self.assertEqual(response.status_code, 200)

    def test_unsuccessful_login_raises_form_error(self):
        ''' If user enters wrong password form error should be displayed '''

        response = self.client.post(reverse('users:login'), {
                                    'username': 'user', 'password': 'Password'}, follow=True)

        return self.assertFormError(response, 'form', None,
                                    'Please enter a correct username and password. Note that both fields may be case-sensitive.')

    def test_successful_login_redirects_to_home_page(self):
        ''' Check if successful login redirects to the home page '''

        response = self.client.post(
            reverse('users:login'), {'username': 'staff', 'password': 'Password1'}, follow=True)
        return self.assertRedirects(response, reverse('library:home'), status_code=302, target_status_code=200)

    # Test user account deletion
    def test_get_delete_user_displays_confirm_deletion(self):
        '''Get request to delete_user asks for confirmation'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        user = User.objects.get(pk=1)
        response = self.client.get(reverse('users:delete', kwargs={'pk': user.pk}))
        self.assertContains(response, f'Do you really want to delete the user "{user}"?')

    def test_staff_member_can_delete_user_account(self):
        '''Staff member should be able to remove user acccount and should be redirected to home page'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        user = User.objects.create(username='user1',
                                   first_name='j', last_name='p', address='x', born='2023-05-11',
                                   email='user1@x.com')
        response = self.client.post(reverse('users:delete', kwargs={'pk': user.pk}), follow=True)
        queryset = User.objects.filter(pk=user.pk)
        self.assertEqual(queryset.count(), 0)
        self.assertRedirects(response, reverse('library:home'),
                             status_code=302, target_status_code=200)

    def test_user_cannot_delete_account(self):
        '''Removing acccounts is forbidden for none staff members '''

        user = User.objects.get(pk=1)
        staff = User.objects.get(pk=2)
        self.client.force_login(user)
        response = self.client.post(reverse('users:delete', kwargs={'pk': staff.pk}), follow=True)
        queryset = User.objects.filter(pk=user.pk)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(response.status_code, 403)

    def test_user_account_can_not_be_deleted(self):
        '''User account can not be deleted if user have borrowed books'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        user = User.objects.get(pk=1)
        response = self.client.post(reverse('users:delete', kwargs={'pk': user.pk}), follow=True)
        queryset = User.objects.filter(pk=user.pk)
        self.assertEqual(queryset.count(), 1)
        self.assertRedirects(response, reverse('users:profile', kwargs={'pk': user.pk}),
                             status_code=302, target_status_code=200)

    def test_delete_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        user = User.objects.get(pk=1)
        response = self.client.post(reverse('users:delete', kwargs={'pk': user.pk}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('users:delete', kwargs={'pk': user.pk}),
                                    status_code=302, target_status_code=200)

    # Test user account update
    def test_get_update_page(self):
        '''Get update page should return status code 200'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        user = User.objects.get(pk=1)
        response = self.client.get(reverse('users:delete', kwargs={'pk': user.pk}))
        return self.assertEqual(response.status_code, 200)

    def test_staff_member_can_update_user_account(self):
        '''Staff member should be able to update user acccount and should be redirected to the user profile'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        user = User.objects.get(pk=1)
        response = self.client.post(reverse('users:update', kwargs={'pk': user.pk}), { 'telefon_number': 12345678, 'email': 'abc1@op.com', 'first_name': 'test', 'last_name': 'a', 'born': '2023-04-23', 'address': 'xxx', }, follow=True)
        user = User.objects.get(pk=1)
        self.assertEqual(user.first_name, 'test')
        self.assertRedirects(response, reverse('users:profile', kwargs={'pk': user.pk}),
                             status_code=302, target_status_code=200)

    def test_user_cannot_update_account(self):
        '''Updating accounts is forbidden for none staff members '''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(reverse('users:update', kwargs={'pk': user.pk}), follow=True)
        return self.assertEqual(response.status_code, 403)

    def test_update_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        user = User.objects.get(pk=1)
        response = self.client.post(reverse('users:update', kwargs={'pk': user.pk}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('users:update', kwargs={'pk': user.pk}),
                                    status_code=302, target_status_code=200)

    # Test user account change password
    def test_get_password_change_page(self):
        '''Get password change page should return status code 200 for logged in users'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('users:password_change'))
        return self.assertEqual(response.status_code, 200)

    def test_account_owner_can_change_password(self):
        '''Account owner should be able to change password and should be redirected to the confirmation page'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(reverse('users:password_change'), {
                                    'old_password': 'Password1', 'new_password1': '2mojeHasloDoTestow', 'new_password2': '2mojeHasloDoTestow'}, follow=True)
        # Check redirection
        self.assertRedirects(response, reverse('users:password_change_done'),
                             status_code=302, target_status_code=200)

        # Logout and try login using the new password
        self.client.logout()
        log = self.client.login(username='user', password='2mojeHasloDoTestow')
        self.assertTrue(log)

    def test_change_password_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        user = User.objects.get(pk=1)
        response = self.client.post(reverse('users:update', kwargs={'pk': user.pk}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('users:update', kwargs={'pk': user.pk}),
                                    status_code=302, target_status_code=200)

    def test_change_password_raises_form_error(self):
        ''' If user enters wrong password form error should be displayed '''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(reverse('users:password_change'), {
                                    'old_password': 'Password', 'new_password1': '2mojeHasloDoTestow', 'new_password2': '2mojeHasloDoTestow'}, follow=True)

        return self.assertFormError(response, 'form', 'old_password',
                                    'Your old password was entered incorrectly. Please enter it again.')

    # Test registration
    def test_get_registration_page(self):
        '''Get the registration page should return status code 200 for staff members'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.get(reverse('users:registration'))
        return self.assertEqual(response.status_code, 200)

    def test_get_registration_page_forbidden(self):
        '''Get the registration page is forbidden for none staff members'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('users:registration'))
        return self.assertEqual(response.status_code, 403)

    def test_registration_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        user = User.objects.get(pk=1)
        response = self.client.get(reverse('users:registration'))
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('users:registration'),
                                    status_code=302, target_status_code=200)

    def test_staff_member_register_new_user_default_photo(self):
        '''Staff member should be able to register a new user  and should be redirected to the user profile'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.post(reverse('users:registration'), {'username':
                                    'abc', 'password1': '2mojeHasloDoTestow', 'password2': '2mojeHasloDoTestow', 'telefon_number': 12345678, 'email': 'abc@x.com', 'first_name': 'a', 'last_name': 'a', 'born': '2023-04-23', 'address': 'xxx'}, follow=True)
        queryset = User.objects.filter(username='abc')
        self.assertEqual(queryset.count(), 1)
        user = queryset.get()
        self.assertEqual(user.profile_picture, 'default.jpeg')
        self.assertRedirects(response, reverse('users:profile', kwargs={'pk': queryset.get().pk}),
                             status_code=302, target_status_code=200)

    def test_staff_member_register_new_user_photo_upload(self):
        '''Staff member should be able to register a new user and should be redirected to the user profile'''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        file = open('library/static/library/test_files/test_picture.png', 'rb')
        response = self.client.post(reverse('users:registration'), {'username':
                                    'abc', 'password1': '2mojeHasloDoTestow', 'password2': '2mojeHasloDoTestow', 'email': 'abc@x.com', 'telefon_number': 12345678,'first_name': 'a', 'last_name': 'a', 'born': '2023-04-23', 'address': 'xxx', 'profile_picture': file}, follow=True)

        file.close()
        queryset = User.objects.filter(username='abc')
        self.assertEqual(queryset.count(), 1)
        user = queryset.get()
        self.assertIn('test_picture.png', user.profile_picture.name)
        self.assertRedirects(response, reverse('users:profile', kwargs={'pk': queryset.get().pk}),
                             status_code=302, target_status_code=200)

        # Remove uploaded picture from media folder
        path = os.path.join(MEDIA_URL, user.profile_picture.name)
        os.remove(path[1:])

    def test_registration_raises_form_error(self):
        ''' If user enters email address which is already in use form error should be displayed '''

        staff = User.objects.get(pk=2)
        self.client.force_login(staff)
        response = self.client.post(reverse('users:registration'), {'username':
                                    'abc', 'password1': '2mojeHasloDoTestow', 'password2': '2mojeHasloDoTestow', 'email': 'user@x.com', 'first_name': 'a', 'last_name': 'a', 'born': '2023-04-23', 'address': 'xxx'}, follow=True)
        return self.assertFormError(response, 'form', 'email',
                                    'User with this Email already exists.')
