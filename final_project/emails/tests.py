from django.test import TestCase
import unittest
from emails.models import Email
from .models import User
import datetime
from django.test import Client
from django.urls import reverse
from django.db.models import Avg, Max, Min, Sum, Count
from django.test import tag
import pathlib


class EmailTestCase(TestCase):
    def setUp(self):
        # Create client object as attribute
        self.client = Client()

        # Create users
        user1 = User.objects.create(username='user1',
                                    first_name='j', last_name='p', address='x', born='2023-05-11',
                                    email='user1@x.com')
        user1.set_password('Password1')
        user1.save()

        user2 = User.objects.create(username='user2',
                                    first_name='j', last_name='p', address='x', born='2023-05-11',
                                    email='user2@x.com')
        user2.set_password('Password1')
        user2.save()

        user3 = User.objects.create(username='user3',
                                    first_name='j', last_name='p', address='x', born='2023-05-11',
                                    email='user3@x.com')
        user3.set_password('Password1')
        user3.save()

        staff = User.objects.create(username='staff',
                                    first_name='s', last_name='m', address='x', born='2023-05-11',
                                    email='staff@x.com', staff_member=True)
        staff.set_password('Password1')
        staff.save()

        # Create email for one recipient
        recipients = [user2]
        users = list(recipients) + [user1]
        for user in users:
            email = Email(
                user=user,
                sender=user1,
                subject='My subject',
                body='My body',
                read=user == user1
            )
            email.save()
            for recipient in recipients:
                email.recipients.add(recipient)
            email.save()

        # Create email for two recipients
        recipients = [user2, staff]
        users = list(recipients) + [user1]
        for user in users:
            email = Email(
                user=user,
                sender=user1,
                subject='My subject 2 recipients',
                body='My body 2 recipients',
                read=user == user1
            )
            email.save()
            for recipient in recipients:
                email.recipients.add(recipient)
            email.save()

        # Create an archived email
        recipients = [user2, staff]
        users = list(recipients) + [user1]
        for user in users:
            email = Email(
                user=user,
                sender=user1,
                subject='My subject archived email',
                body='My body archived email',
                read=True,
                archived=True
            )
            email.save()
            for recipient in recipients:
                email.recipients.add(recipient)
            email.save

    # Test inbox
    def test_get_email_inbox_unlogged_users(self):
        '''Get method is not allowed for unlogged users, they should be redirected to the home page'''

        response = self.client.get(reverse('emails:email_inbox'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('emails:email_inbox'),
                                    status_code=302, target_status_code=200)

    def test_welcome_emails_has_been_sent(self):
        '''Each user receives welcome email after registration'''

        user = User.objects.get(username='user3')
        return self.assertEqual(user.emails_received.count(), 1)

    def test_get_email_inbox_loggedin_users(self):
        '''Received emails should be returned for logged in users'''

        user = User.objects.get(username='user2')
        self.client.force_login(user)
        response = self.client.get(reverse('emails:email_inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('object_list').count(), 3)
        self.assertEqual(response.context.get('unread_messages'), 3)

    # Test emails sent
    def test_get_email_sent_unlogged_users(self):
        '''Get method is not allowed for unlogged users, they should be redirected to the home page'''

        response = self.client.get(reverse('emails:email_sent'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('emails:email_sent'),
                                    status_code=302, target_status_code=200)

    def test_get_email_sent_loggedin_users(self):
        '''Sent emails should be returned for logged in users'''

        user = User.objects.get(username='user1')
        self.client.force_login(user)
        response = self.client.get(reverse('emails:email_sent'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('object_list').count(), 2)
        self.assertEqual(response.context.get('unread_messages'), 1)

    # Test archived
    def test_get_email_archived_unlogged_users(self):
        '''Get method is not allowed for unlogged users, they should be redirected to the home page'''

        response = self.client.get(reverse('emails:email_archive'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('emails:email_archive'),
                                    status_code=302, target_status_code=200)

    def test_get_email_archived_loggedin_users(self):
        '''Archived emails and number of unread messages should be returned'''

        user = User.objects.get(username='user2')
        self.client.force_login(user)
        response = self.client.get(reverse('emails:email_archive'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('object_list').count(), 1)
        self.assertEqual(response.context.get('unread_messages'), 3)

    # Test email detail
    def test_get_email_detail_unlogged_users(self):
        '''Get method is not allowed for unlogged users, they should be redirected to the home page'''

        response = self.client.get(reverse('emails:email_details', kwargs={'pk': 2}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('emails:email_details', kwargs={'pk': 2}),
                                    status_code=302, target_status_code=200)

    def test_get_unarchived_email_detail_loggedin_users(self):
        '''The page should contain a delete button, an archive button, and hidden unarchive button and number of unread messages. After page was loaded email should be markt as red'''

        user = User.objects.get(username='user2')
        self.client.force_login(user)
        email = user.emails.get(subject='My subject')
        self.assertEqual(email.user, user)
        # Assert that email is unread
        self.assertFalse(email.read)
        response = self.client.get(reverse('emails:email_details', kwargs={'pk': email.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('unread_messages'), 2)
        self.assertContains(
            response, '<button class="btn btn-outline-danger" type="button" name="button">Delete</button>', status_code=200, html=True)
        self.assertContains(
            response, f'<button id="archiveBtn" data-emailpk={email.pk} class="btn btn-outline-secondary" type="button" name="button">Archive</button>', status_code=200, html=True)
        self.assertContains(
            response, f'<button id="unarchiveBtn" data-emailpk={email.pk} class="d-none btn btn-outline-secondary" type="button" name="button">Unarchive</button>', status_code=200, html=True)

        # Assert that email was marked as red
        email = user.emails.get(subject='My subject')
        self.assertTrue(email.read)

    def test_get_archived_email_detail_loggedin_users(self):
        '''The page should contain a delete button, an unarchive button, and hidden archive button and number of unread messages'''

        user = User.objects.get(username='user2')
        self.client.force_login(user)
        email = Email.objects.filter(archived=True).first()
        response = self.client.get(reverse('emails:email_details', kwargs={'pk': email.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('unread_messages'), 3)
        self.assertContains(
            response, '<button class="btn btn-outline-danger" type="button" name="button">Delete</button>', status_code=200, html=True)
        self.assertContains(
            response, f'<button id="archiveBtn" data-emailpk={email.pk} class="d-none btn btn-outline-secondary" type="button" name="button">Archive</button>', status_code=200, html=True)
        self.assertContains(
            response, f'<button id="unarchiveBtn" data-emailpk={email.pk} class="btn btn-outline-secondary" type="button" name="button">Unarchive</button>', status_code=200, html=True)

    def test_get_email_doesnt_exists(self):
        ''' Response code status should be 404 '''

        user = User.objects.get(username='user2')
        self.client.force_login(user)
        response = self.client.get(reverse('emails:email_details', kwargs={'pk': 1000000}))
        self.assertEqual(response.status_code, 404)

    def test_get_email_belongs_to_another_user(self):
        ''' Response code status should be 403 '''

        user = User.objects.get(username='staff')
        self.client.force_login(user)
        email = Email.objects.filter(subject='My subject').first()
        response = self.client.get(reverse('emails:email_details', kwargs={'pk': email.pk}))
        self.assertEqual(response.status_code, 403)

    # Test compose an email
    def test_get_compose_email(self):
        '''Get the compose email page should return status code 200 for logged in users'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('emails:email_compose'))
        return self.assertEqual(response.status_code, 200)

    def test_get_compose_email_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        response = self.client.get(reverse('emails:email_compose'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('emails:email_compose'),
                                    status_code=302, target_status_code=200)

    def test_compose_email_one_recipient(self):
        ''' Email should be sent. Success message should be displayed'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(reverse('emails:email_compose'), {'sender': user.email, 'recipients':
                                    'user2@x.com', 'subject': 'Test subject', 'body': 'Test body'}, follow=True)

        # Check if recipient received the email
        recipient = User.objects.get(email='user2@x.com')
        recipient_email_query = Email.objects.filter(user=recipient, subject='Test subject')
        self.assertEqual(recipient_email_query.count(), 1)

        # Check if sender received copy of the email
        sender_email_query = Email.objects.filter(user=user, subject='Test subject')
        self.assertEqual(sender_email_query.count(), 1)

        # Check if sender was redirected to his own copy of the email
        sender_email_query = Email.objects.filter(user=user, subject='Test subject')
        self.assertRedirects(response, reverse('emails:email_details', kwargs={'pk': sender_email_query.get().pk}),
                             status_code=302, target_status_code=200)

        self.assertContains(response, 'Email has been sent succesfully.')

    def test_compose_email_two_recipients(self):
        ''' Email should be sent. Success message should be displayed'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(reverse('emails:email_compose'), {'sender': user.email, 'recipients':
                                    'user2@x.com, user3@x.com', 'subject': 'Test two recipients', 'body': 'Test body'}, follow=True)

        # Check if recipients received the email
        recipient1 = User.objects.get(email='user2@x.com')
        recipient1_email_query = Email.objects.filter(
            user=recipient1, subject='Test two recipients')
        self.assertEqual(recipient1_email_query.count(), 1)
        recipient2 = User.objects.get(email='user3@x.com')
        recipient2_email_query = Email.objects.filter(
            user=recipient2, subject='Test two recipients')
        self.assertEqual(recipient2_email_query.count(), 1)

        # Check if sender received email copy
        sender_email_query = Email.objects.filter(user=user, subject='Test two recipients')
        self.assertEqual(sender_email_query.count(), 1)

        # Check if sender was redirected to his own copy of the email
        sender_email_query = Email.objects.filter(user=user, subject='Test two recipients')
        self.assertRedirects(response, reverse('emails:email_details', kwargs={'pk': sender_email_query.get().pk}),
                             status_code=302, target_status_code=200)

        self.assertContains(response, 'Email has been sent succesfully.')

    def test_compose_email_recipient_not_exists(self):
        ''' Email should not be sent. Form error message should be displayed '''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(reverse('emails:email_compose'), {'sender': user.email, 'recipients':
                                    'user20@x.com', 'subject': 'Test Error', 'body': 'Test body'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form',
                             'recipients', 'There is no user with such an email address: user20@x.com.')

        # Check if sender did not receive copy of the mail
        sender_email_query = Email.objects.filter(user=user, subject='Test Error')
        self.assertEqual(sender_email_query.count(), 0)

    def test_compose_email_invalid_email_address(self):
        ''' Email should not be sent. Form error message should be raised '''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(reverse('emails:email_compose'), {
                                    'recipients': 'test@op, user2@x.com', 'subject': 'Test Error'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form',
                             'recipients', '"test@op" is not a valid email address.')

        # Check if sender did not receive copy of the mail
        sender_email_query = Email.objects.filter(user=user, subject='Test Error')
        self.assertEqual(sender_email_query.count(), 0)

        # Check if the other user did not receive copy of the email
        recipient = User.objects.get(email='user2@x.com')
        sender_email_query = Email.objects.filter(user=recipient, subject='Test Error')
        self.assertEqual(sender_email_query.count(), 0)

    def test_compose_email_no_recipients_provided(self):
        ''' Email should not be sent. Form error message should be raised '''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.post(reverse('emails:email_compose'), {
                                    'recipients': '', 'subject': 'Test Error'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form',
                             'recipients', 'This field is required.')

    # Test reply email
    def test_get_reply_email_first_reply(self):
        '''Get the reply email page should return status code 200. Should contain initial data'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        email = Email.objects.get(user=user, subject='My subject')
        response = self.client.get(reverse('emails:email_reply', kwargs={'email_pk': email.pk}))
        initial = response.context.get('form').initial
        recipient = User.objects.get(pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(initial.get('sender'), user.email)
        self.assertEqual(initial.get('recipients'), recipient.email)
        self.assertEqual(initial.get('subject'), 'Re: My subject')
        self.assertContains(response, 'My body')

    def test_get_reply_email_second_reply(self):
        '''Get the reply email page should return status code 200. Should contain initial data. Subject should have prefix Re: re:'''

        user1 = User.objects.get(pk=1)
        user2 = User.objects.get(pk=2)
        self.client.force_login(user2)

        # Create an first reply email
        recipients = [user2]
        users = list(recipients) + [user1]
        for user in users:
            email = Email(
                user=user,
                sender=user1,
                subject='Re: First reply email',
                body='My body',
                read=user == user1
            )
            email.save()
            for recipient in recipients:
                email.recipients.add(recipient)
            email.save()

        # Get user2's copy of the 1 reply email
        email = Email.objects.get(user=user2, subject='Re: First reply email')

        # Get the form page to create second reply
        response = self.client.get(reverse('emails:email_reply', kwargs={'email_pk': email.pk}))

        # Check if the form is correctly prefilled
        initial = response.context.get('form').initial
        self.assertEqual(response.status_code, 200)
        self.assertEqual(initial.get('sender'), user2.email)
        self.assertEqual(initial.get('recipients'), user1.email)
        self.assertEqual(initial.get('subject'), 'Re: re: First reply email')
        self.assertContains(response, 'My body')

    def test_get_reply_email_third_reply(self):
        '''Get the reply email page should return status code 200. Should contain initial data. Subject should have prefix Re: re:'''

        user1 = User.objects.get(pk=1)
        user2 = User.objects.get(pk=2)
        self.client.force_login(user2)

        # Create an second reply email
        recipients = [user2]
        users = list(recipients) + [user1]
        for user in users:
            email = Email(
                user=user,
                sender=user1,
                subject='Re: re: Second reply email',
                body='My body',
                read=user == user1
            )
            email.save()
            for recipient in recipients:
                email.recipients.add(recipient)
            email.save()

        # Get user2's copy of the 2 reply email
        email = Email.objects.get(user=user2, subject='Re: re: Second reply email')

        # Get the form page to create third reply
        response = self.client.get(reverse('emails:email_reply', kwargs={'email_pk': email.pk}))

        # Check if the form is correctly prefilled
        initial = response.context.get('form').initial
        self.assertEqual(response.status_code, 200)
        self.assertEqual(initial.get('sender'), user2.email)
        self.assertEqual(initial.get('recipients'), user1.email)
        self.assertEqual(initial.get('subject'), 'Re: re: Second reply email')
        self.assertContains(response, 'My body')

    def test_get_reply_email_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        user = User.objects.get(pk=2)
        email = Email.objects.get(user=user, subject='My subject')
        response = self.client.get(reverse('emails:email_reply', kwargs={
                                   'email_pk': email.pk}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('emails:email_reply', kwargs={
            'email_pk': email.pk}),
            status_code=302, target_status_code=200)

    def test_reply_email_one_recipient(self):
        ''' Recipients should receive email. Sender should be redirected to the email details. Success message should be displayed'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)

        # Get email initial values
        email = Email.objects.get(user=user, subject='My subject')
        response_get = self.client.get(reverse('emails:email_reply', kwargs={'email_pk': email.pk}))
        initial = response_get.context.get('form').initial
        response = self.client.post(reverse('emails:email_reply', kwargs={
            'email_pk': email.pk}), {'sender': initial.get('sender'), 'recipients':
                                     initial.get('recipients'), 'subject': initial.get('subject'), 'body': 'Test body' + initial.get('body')}, follow=True)

        # Check if recipient and sender received email copy
        sender = User.objects.get(email=initial.get('sender'))
        sender_email_query = Email.objects.filter(user=sender, subject=initial.get('subject'))
        self.assertEqual(sender_email_query.count(), 1)
        recipient = User.objects.get(email=initial.get('recipients'))
        recipient_email_query = Email.objects.filter(user=recipient, subject=initial.get('subject'))
        self.assertEqual(recipient_email_query.count(), 1)

        # Check if sender was redirected to his own copy of the email
        sender_email_query = Email.objects.filter(user=user, subject='Re: My subject')
        self.assertRedirects(response, reverse('emails:email_details', kwargs={'pk': sender_email_query.get().pk}),
                             status_code=302, target_status_code=200)
        self.assertContains(response, 'Email has been sent succesfully.')

    def test_reply_email_two_recipients(self):
        '''Recipients should receive the email. Sender should be redirected to the email details. Success message should be displayed'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)

        # Get email initial values
        email = Email.objects.get(user=user, subject='My subject 2 recipients')
        response_get = self.client.get(reverse('emails:email_reply', kwargs={'email_pk': email.pk}))
        initial = response_get.context.get('form').initial

        response = self.client.post(reverse('emails:email_reply', kwargs={
            'email_pk': email.pk}), {'sender': initial.get('sender'), 'recipients':
                                     initial.get('recipients'), 'subject': initial.get('subject'), 'body': 'Test body' + initial.get('body')}, follow=True)

        # Check if recipient and sender received email copy
        sender = User.objects.get(email=initial.get('sender'))
        sender_email_query = Email.objects.filter(
            user=sender, subject='Re: My subject 2 recipients')
        self.assertEqual(sender_email_query.count(), 1)
        recipient = User.objects.get(email=initial.get('recipients'))
        recipient_email_query = Email.objects.filter(user=recipient, subject=initial.get('subject'))
        self.assertEqual(recipient_email_query.count(), 1)

        # Check if sender was redirected to his own copy of the email
        sender_email_query = Email.objects.filter(user=user, subject='Re: My subject 2 recipients')
        self.assertRedirects(response, reverse('emails:email_details', kwargs={'pk': sender_email_query.get().pk}),
                             status_code=302, target_status_code=200)
        self.assertContains(response, 'Email has been sent succesfully.')

    def test_reply_email_does_not_exists(self):
        ''' Recipient should not receive the email. Response code shhould be 404'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)

        response = self.client.post(reverse('emails:email_reply', kwargs={
            'email_pk': 200}), {'sender': 'user1@x.com', 'recipients':
                                'user2@x.com', 'subject': 'Re: Email does not exists', 'body': 'Test body'}, follow=True)

        # Check if recipient did not receive the email
        recipient = User.objects.get(email='user2@x.com')
        recipient_email_query = Email.objects.filter(
            user=recipient, subject='Re: Email does not exists')
        self.assertEqual(recipient_email_query.count(), 0)

        self.assertEqual(response.status_code, 404)

    def test_reply_email_belongs_to_another_user(self):
        ''' Response should contain an error message '''

        user = User.objects.get(username='staff')
        self.client.force_login(user)
        email = Email.objects.filter(subject='My subject').first()
        response = self.client.post(reverse('emails:email_reply', kwargs={
            'email_pk': email.pk}), {'sender': 'staff@x.com', 'recipients':
                                     'user2@x.com', 'subject': 'Re: Not my email', 'body': 'Test body'}, follow=True)
        self.assertEqual(response.status_code, 403)

    # Test email deletion
    def test_get_delete_email_displays_confirm_deletion(self):
        '''Get delete email request asks for confirmation'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        email = Email.objects.filter(user=user).first()
        response = self.client.get(reverse('emails:email_delete', kwargs={'pk': email.pk}))
        return self.assertContains(
            response, f'Do you really want to delete the email "{email.subject}" sent by "{email.sender}" from the database?')

    def test_email_user_can_delete_email(self):
        '''Email author should be able to remove his own copy of an email and should be redirected to email inbox. Copies of the other users should not be removed'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        email = Email.objects.get(user=user, subject='My subject 2 recipients')
        response = self.client.post(reverse('emails:email_delete', kwargs={'pk': email.pk}))

        # Check if the email was removed
        queryset = Email.objects.filter(pk=email.pk)
        self.assertEqual(queryset.count(), 0)

        # Check if the other copies are available
        user1 = User.objects.get(username='user1')
        user1_copy = Email.objects.get(user=user1, subject='My subject 2 recipients')
        queryset = Email.objects.filter(pk=user1_copy.pk)
        self.assertEqual(queryset.count(), 1)
        staff = User.objects.get(username='staff')
        staff_copy = Email.objects.get(user=staff, subject='My subject 2 recipients')
        queryset = Email.objects.filter(pk=staff_copy.pk)
        self.assertEqual(queryset.count(), 1)

        # Check redirection
        self.assertRedirects(response, reverse('emails:email_inbox'),
                             status_code=302, target_status_code=200)

    def test_user_cannot_delete_email(self):
        '''User can only delete his own copy of an email'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        author = User.objects.get(pk=1)
        email = Email.objects.filter(user=author).first()
        response = self.client.post(reverse('emails:email_delete', kwargs={'pk': email.pk}))
        queryset = Email.objects.filter(pk=email.pk)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(response.status_code, 403)

    def test_delete_email_unlogged_users_are_redirected(self):
        '''Unlogged users should be redirected to the login page'''

        email = Email.objects.get(pk=10)
        response = self.client.get(
            reverse('emails:email_delete', kwargs={'pk': email.pk}), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('emails:email_delete', kwargs={'pk': email.pk}),
                                    status_code=302, target_status_code=200)

    def test_delete_email_doesnt_exists(self):
        '''Response status should be 404'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        response = self.client.post(reverse('emails:email_delete', kwargs={'pk': 10000000}))
        self.assertEqual(response.status_code, 404)

    def test_delete_email_belongs_to_another_user(self):
        ''' Response code status should be 403 '''

        user = User.objects.get(username='staff')
        self.client.force_login(user)
        email = Email.objects.filter(subject='My subject').first()
        response = self.client.post(reverse('emails:email_delete', kwargs={'pk': email.pk}))
        self.assertEqual(response.status_code, 403)

    # Email archive
    def test_get_email_archive_logged_users(self):
        '''Get method is not allowed should return "Wrong request." message.'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('emails:update_email_archive'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), 'Wrong request.')

    def test_get_email_archive_unlogged_users(self):
        '''Get method is not allowed should redirect user to the login page'''

        response = self.client.get(reverse('emails:update_email_archive'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('emails:update_email_archive'),
                                    status_code=302, target_status_code=200)

    def test_email_archive(self):
        '''User should be able archive an email. The other copies of the email should be left unarchived'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        email = Email.objects.get(user=user, subject='My subject 2 recipients')
        response = self.client.post(reverse('emails:update_email_archive'),
                                    {'emailpk': email.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Check if the email was archived
        email = Email.objects.get(user=user, subject='My subject 2 recipients')
        self.assertTrue(email.archived)

        # Check if the other copy of the email was not archived
        staff = User.objects.get(username='staff')
        email = Email.objects.get(user=staff, subject='My subject 2 recipients')
        self.assertFalse(email.archived)

    def test_email_archive_email_doesnt_exists(self):
        '''Response status should be 404'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        response = self.client.post(reverse('emails:update_email_archive'),
                                    {'emailpk': 100}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_archive_email_belongs_to_another_user(self):
        ''' Response should contain an error message '''

        user = User.objects.get(username='staff')
        self.client.force_login(user)
        email = Email.objects.filter(subject='My subject').first()
        response = self.client.post(reverse('emails:update_email_archive'),
                                    {'emailpk': email.pk}, content_type='application/json')
        self.assertContains(response, 'You can only archive your own emails.',
                            status_code=200, msg_prefix='', html=False)

    # Email unarchive
    def test_get_email_unarchive_logged_users(self):
        '''Get method is not allowed should return "Wrong request." message.'''

        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get(reverse('emails:update_email_unarchive'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), 'Wrong request.')

    def test_get_email_unarchive_unlogged_users(self):
        '''Get method is not allowed should redirect user to the login page'''

        response = self.client.get(reverse('emails:update_email_unarchive'), follow=True)
        return self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('emails:update_email_unarchive'),
                                    status_code=302, target_status_code=200)

    def test_email_unarchive(self):
        '''User should be able unarchive an email. The other copies of the email should be left archived'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        email = Email.objects.get(user=user, subject='My subject archived email')
        response = self.client.post(reverse('emails:update_email_unarchive'),
                                    {'emailpk': email.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Check if the email was unarchived
        email = Email.objects.get(user=user, subject='My subject archived email')
        self.assertFalse(email.archived)

        # Check if the other copy of the email was not unarchived
        staff = User.objects.get(username='staff')
        email = Email.objects.get(user=staff, subject='My subject archived email')
        self.assertTrue(email.archived)

    def test_email_archive_email_doesnt_exists(self):
        '''Response status should be 404'''

        user = User.objects.get(pk=2)
        self.client.force_login(user)
        response = self.client.post(reverse('emails:update_email_unarchive'),
                                    {'emailpk': 100}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_unarchive_email_belongs_to_another_user(self):
        ''' Response should contain an error message '''

        user = User.objects.get(username='staff')
        self.client.force_login(user)
        email = Email.objects.filter(subject='My subject').first()
        response = self.client.post(reverse('emails:update_email_unarchive'),
                                    {'emailpk': email.pk}, content_type='application/json')
        self.assertContains(response, 'You can only unarchive your own emails.',
                            status_code=200, msg_prefix='', html=False)
