from django.shortcuts import render
from django.http import Http404
from . import util
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseBadRequest
import markdown2
from .forms import Entry_Form, Edit_Entry_Form
import random
from django.contrib import messages

def index(request):
    """ Displays all available entries """

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    """ Displays the requested entry page, or raises the 404 error if the entry doesn't exists """

    content = util.get_entry(title)
    if content is None:
        raise Http404(f"\"{title}\" entry doesn\'t exists!")
    return render(request, "encyclopedia/entry.html", {
        "content": markdown2.markdown(content), "title":title
    })


def search(request):
    """" Searches for an encyclopedia entry, returns it or displays all entries. """

    if request.method == "POST":
        query = request.POST.get("q")
        entries = util.list_entries()
        substrings = [i for i in entries if query in i]

        # Redirects to the entry’s page if the query matches the name of an encyclopedia entry
        if query in entries:
            return redirect(reverse("encyclopedia:entry", args=[query]))
        
        # Displays a list of all encyclopedia entries that have the query as a substring
        elif len(substrings) > 0:
            return render(request, "encyclopedia/search.html", {
        "entries": substrings})

        # If there is no match show info message and redirect to the home page to display all entries
        else:  
            messages.add_message(request, messages.INFO, f"Entry \"{query}\" hasn't been found!")
            return redirect(reverse("encyclopedia:index"))
    return HttpResponseBadRequest("Wrong request. Only post request is allowed!")


def create(request):
    """ Creates a new entry, and takes the user to the new entry’s page. """

    # Populate the form with data if there was a post request, else create an empty form
    form = Entry_Form(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            title = form.cleaned_data.get("title")
            content = form.cleaned_data.get("content")

            # Save the data
            util.save_entry(title, content)
            return redirect(reverse("encyclopedia:entry", args=[title]))
        
    # If from is invalid render the same form and display the errors  
    return render(request, "encyclopedia/entry_form.html", {
        "form": form})


def edit(request, title):
    """ Lets users edit an already existing page """

    # If the method is get prepopulate the form with the existing data
    if request.method == "GET":
        data = {"title":title, "content": util.get_entry(title)}
        form = Edit_Entry_Form(initial=data)
        return render(request, "encyclopedia/edit_entry_form.html", {"form": form, "title":title})
    elif request.method == "POST":  

        # Save the edited entry if the form is valis, otherwise display errors
        form = Edit_Entry_Form(request.POST)
        if form.is_valid():
            content = form.cleaned_data.get("content")
            util.save_entry(title, content)
            return redirect(reverse("encyclopedia:entry", args=[title]))
        return render(request, "encyclopedia/edit_entry_form.html", {"form": form, "title":title})
    return HttpResponseBadRequest("Wrong request!")


def get_random(request):
    """ Takes user to a random encyclopedia entry. """

    if request.method == "GET":
        entry = random.choice(util.list_entries())
        return redirect(reverse("encyclopedia:entry", args=[entry]))
    return HttpResponseBadRequest("Wrong request. Only post request is allowed!")
