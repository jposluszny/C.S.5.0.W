from django.forms import ModelForm
from .models import Listing, Bid, Comment


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        exclude = ['user', 'created']


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
