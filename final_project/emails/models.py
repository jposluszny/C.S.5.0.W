from django.db import models
from users.models import User


class Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emails')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL,
                               related_name='emails_sent', null=True)
    recipients = models.ManyToManyField(User, related_name='emails_received')
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('emails:email_details', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.sender} on {self.timestamp}'
