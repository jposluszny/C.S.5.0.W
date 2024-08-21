from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Loan, History
from emails.models import Email
from users.models import User
from django.core.signals import request_finished


@receiver(post_delete, sender=Loan)
def my_handler(sender, instance, using, **kwargs):
    ''' Creates history loan object after loan object was deleted '''

    if instance.status != 'rejected':
        History.objects.create(book=instance.book, user=instance.user,
                               loan_date=instance.loan_date, return_date=instance.return_date, fee=instance.fee,
                               status='returned', can_renew=instance.can_renew, is_overdue=instance.is_overdue)


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    '''Sends welcome email'''

    if created:
        email = Email(user=instance, subject='Welcome to our library',
                      body=f'Hello {instance.username}! \n  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus id fermentum elit. Aenean ornare porta sagittis.\n\nKind Regards\nLibrary Staff')
        email.save()
        email.recipients.add(instance)
        email.save()
