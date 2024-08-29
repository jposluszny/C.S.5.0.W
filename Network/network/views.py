from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import User, Post
from .forms import PostForm
from django.http import Http404
from django.http import JsonResponse
import json
from django.core.paginator import Paginator


def index(request):
    '''Creates a new form, saves a new post and gets a list of all posts'''

    form = PostForm(request.POST or None)

    # Save a new post
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form = PostForm()
    posts = Post.objects.all().order_by('-created_on')

    # Create pagination
    page_nr = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)
    page = paginator.page(page_nr)
    return render(request, "network/index.html", {'form': form, 'page': page})


@login_required
def following(request):
    '''Displays posts made by users that the current user follows.'''

    user = request.user
    posts = Post.objects.filter(author__in=user.followed.all()).order_by('-created_on')

    # Create pagination
    page_nr = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)
    page = paginator.page(page_nr)
    return render(request, "network/following.html", {'page': page})


def profile(request, user):
    ''' Gets all users\' posts, followers and followed users.'''

    requested_profile = get_object_or_404(User, username=user)
    posts = requested_profile.posts.all().order_by('-created_on')
    followed = requested_profile.followed.all()
    followers = requested_profile.followers.all()

    # Create pagination
    page_nr = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)
    page = paginator.page(page_nr)
    context = {'requested_profile': requested_profile, 'page': page,
               'followers': followers, 'followed': followed}

    return render(request, "network/profile.html", context)


@login_required
def toggle(request):
    ''' Toggles whether current user follows the user’s posts and
        returns the number of followers.'''

    requested_profile_name = request.GET.get('requested_profile')
    requested_profile = get_object_or_404(User, username=requested_profile_name)
    user = request.user
    if requested_profile in user.followed.all():
        user.followed.remove(requested_profile)
    else:
        user.followed.add(requested_profile)
    followers = str(len(requested_profile.followers.all()))
    return HttpResponse(followers)


def like(request):
    ''' Updates the like count '''

    post_pk = request.GET.get('post')
    post = get_object_or_404(Post, pk=post_pk)
    type = request.GET.get('type')
    user = request.user
    message = ''
    if user.is_authenticated:
        if type == 'like':

            # Check if user has already liked the post
            if user in post.likes.all():
                message = 'You have already liked the post.'

            # If not add user' like and remove unlike
            else:
                post.likes.add(user)
                if user in post.unlikes.all():
                    post.unlikes.remove(user)
        else:
            # Check if user has already unliked the post
            if user in post.unlikes.all():
                message = 'You have already unliked the post.'

            # If not add user' unlike and remove like
            else:
                post.unlikes.add(user)
                if user in post.likes.all():
                    post.likes.remove(user)
    else:
        message = 'You must be logged in to like the post!'
    return JsonResponse({'likes': len(post.likes.all()), 'unlikes': len(post.unlikes.all()),
                        'message': message})


@login_required
def edit(request):
    ''' Gets an edited post's content, post's pk and updates the database'''

    if request.method == 'PUT':
        data = json.loads(request.body)
        post = get_object_or_404(Post, pk=data['pk'])
        post.content = data['content']
        post.save()
        return JsonResponse({'result': True}, status=200)
    return JsonResponse({'error': 'error'}, status=400)


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
