from django.db import models
from django.urls import reverse
import datetime
from users.models import User
from django.core.exceptions import ValidationError


class Book(models.Model):
    isbn = models.IntegerField(unique=True)
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=256)
    description = models.TextField(
        default='''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam tortor mauris, maximus semper volutpat vitae, varius placerat dui. Nunc consequat dictum est, at vestibulum est hendrerit at. Mauris suscipit neque ultrices nisl interdum accumsan. Sed euismod, ligula eget tristique semper, lectus est pellentesque dui, sit amet rhoncus leo mi nec orci. Curabitur hendrerit, est in ultricies interdum, lacus lacus aliquam mauris, vel vestibulum magna nisl id arcu. Cras luctus tellus ac convallis venenatis. Cras consequat tempor tincidunt. Proin ultricies purus mauris, non tempor turpis mollis id. Nam iaculis risus mauris, quis ornare neque semper vel.'''
    )
    year = models.IntegerField()

    class Meta:
        ordering = ['title']

    def get_absolute_url(self):
        return reverse('library:book_details', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.title} by {self.author}'


class Loan(models.Model):
    STATUS_CHOICES = (('accepted', 'accepted'), ('pending', 'pending'))

    book = models.OneToOneField(Book, related_name='loan', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='borrowing', on_delete=models.CASCADE)
    loan_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    can_renew = models.BooleanField(default=False)

    def clean(self):
        if self.status == 'accepted':
            if not self.loan_date:
                raise ValidationError({
                    'loan_date': ValidationError('Accepted loan must have loan date.')})
            if not self.return_date:
                raise ValidationError({
                    'return_date': ValidationError('Accepted loan must have return date.')})
            if self.loan_date > self.return_date:
                raise ValidationError({
                    'return_date': ValidationError('Loan date can not be greater than return date.')})

    @property
    def is_overdue(self):
        if self.status == 'accepted':
            now = datetime.date.today()
            if self.return_date < now:
                return True
        return False

    @property
    def fee(self):
        if self.is_overdue:
            now = datetime.date.today()
            delta = now - self.return_date
            f = (delta.days // 14 + 1) * 10
            return f
        return 0

    def __str__(self):
        return f'Request for "{self.book.title}" by {self.book.author} by the user "{self.user}"'


class History(models.Model):
    STATUS_CHOICES = (('returned', 'returned'),  ('rejected', 'rejected'))
    book = models.ForeignKey(Book, related_name='history_loans', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='history_borrowing', on_delete=models.CASCADE)
    loan_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='returned')
    fee = models.IntegerField(default=0)
    can_renew = models.BooleanField()
    is_overdue = models.BooleanField()
    reject_message = models.TextField(blank=True, default='')

    def __str__(self):
        return f'{self.book} borrowed by {self.user}'


class Book_Review(models.Model):
    class Meta:
        ordering = ['-creation_date']

    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author} on {self.creation_date}'
