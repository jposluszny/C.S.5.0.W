from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .forms import ListingForm, BidForm, CommentForm
from .models import User, Listing, Bid
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request):
    # Renders all active bids
    bids = Bid.objects.filter(active=True).order_by('-created')
    return render(request, "auctions/index.html", {'bids': bids})


def watchlist(request):
    user = User.objects.get(username=request.user)

    # Adds/removes listing to/from watchlist
    if request.method == 'POST':
        add = request.POST.get('add')
        remove = request.POST.get('remove')
        if add:
            listing = Listing.objects.get(pk=add)
            user.watchlist.add(listing)
        if remove:
            listing = Listing.objects.get(pk=remove)
            user.watchlist.remove(listing)
        return HttpResponseRedirect(reverse('watchlist'))
    else:
        # Gets all listing from users' watchlist
        watchlist = user.watchlist.all().order_by('title')

        # Creates list of bids for watchlist both active and closed
        bids = []
        for listing in watchlist:
            bid = Bid.objects.filter(listing=listing).order_by('-bid')[0]
            bids.append(bid)
        return render(request, "auctions/watchlist.html", {'bids': bids})


def categories(request, category=None):
    # Gets all names of saved categories
    categories = Listing.objects.values('category').exclude(
        category='').distinct().order_by('category')

    # if no category provided render all bids
    if not category:
        bids = Bid.objects.filter(active=True).order_by('-created')

    # Gets all bids of required category
    else:
        query = categories.filter(category__iexact=category).values('pk')
        bids = Bid.objects.filter(listing__in=query).filter(active=True).order_by('-created')
    return render(request, "auctions/categories.html", {'bids': bids, 'categories': categories})


@login_required
def create(request):
    form = ListingForm(request.POST or None)
    if request.method == 'POST':
        form.instance.user = request.user
        if form.is_valid():
            listing = form.save(commit=False)
            listing.category = listing.category.capitalize()
            listing.save()
            bid = Bid(user=form.instance.user, listing=listing, bid=listing.starting_bid)
            bid.save()
            return HttpResponseRedirect(reverse('index'))
    return render(request, 'auctions/create.html', {'form': form})


def listing(request, pk):

    # Gets a listing, create forms
    listing = get_object_or_404(Listing, pk=pk)
    form_comment = CommentForm(request.POST or None)
    form = BidForm(request.POST or None)

    # Checks if user is watching the listing
    try:
        user = User.objects.get(username=request.user)
    except:
        user = None
    if user:
        in_watchlist = listing in user.watchlist.all()
    else:
        in_watchlist = False

    # Gets all bids for the listing
    bids = listing.bid_set.all().order_by('-created')
    if request.method == 'POST' and request.POST.get('close'):

        # Closes the bid
        for bid in bids:
            bid.active = False
            bid.save()
        bids[0].user.wins.add(listing)
        return HttpResponseRedirect(reverse('listing', args=[pk]))

    # Places a new bid
    elif request.method == 'POST' and request.POST.get('place'):
        if form.is_valid():

            # Checks if the bid is at least as large as the starting bid
            if len(bids) == 1:
                if form.cleaned_data.get('bid') < bids[0].bid:
                    messages.error(
                        request, f'The bid must be at least as large as the starting bid: {bids[0].bid}$!')
                    return HttpResponseRedirect(reverse('listing', args=[pk]))

            # Checks if the bid is greater than any other bid
            else:
                if form.cleaned_data.get('bid') <= bids[0].bid:
                    messages.error(request, f'Bid must be higher than {bids[0].bid}$!')
                    return HttpResponseRedirect(reverse('listing', args=[pk]))

            # Sets status to False for all bids
            for i in bids:
                i.active = False
                i.save()

            # Saves a new bid
            bid = form.save(commit=False)
            bid.listing = listing
            bid.user = request.user
            bid.save()
        return HttpResponseRedirect(reverse('listing', args=[pk]))

    # Places a new comment
    elif request.method == 'POST' and request.POST.get('comment'):
        if form_comment.is_valid():
            comment = form_comment.save(commit=False)
            comment.listing = listing
            comment.user = user
            comment.save()
        return HttpResponseRedirect(reverse('listing', args=[pk]))

    comments = Listing.objects.get(pk=pk).comments.all().order_by('-created')
    return render(request, 'auctions/listing.html',
                  {'listing': listing, 'bids': bids, 'form': form, 'comments': comments,
                   'form_comment': form_comment, 'in_watchlist': in_watchlist})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
