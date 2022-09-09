from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import User, Listing

"""
Forms:
"""



"""
Views:
"""
def index(request):
    return render(request, "auctions/index.html")

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

def create_listing(request):
    return render(request, "auctions/create_listing.html")

# Display a listing:
def listing(request, id):
    #Verify that listing exsists:
    try:
        listing = Listing.objects.get(id=id)
    except:
        return HttpResponse("Entry does not exist")
    
    context = {}
    context["listing"] = listing
    context["ended"] = False
    
    if listing.is_finished():
        context["ended"] = True
        return render(request, "auctions/auction.html", context)
    
    # Calculate remaining time:
    time_remaining = listing.end_time - timezone.now()
    context["days"] = time_remaining.days
    context["hours"] = int(time_remaining.seconds/3600)
    context["minutes"] = int(time_remaining.seconds/60 - (context["hours"] * 60))
    #context["bid_form"] = BidForm()
    #context["comment_form"] = CommentForm()

    return render(request, "auctions/listing.html", context)

def categories(request):
    return render(request, "auctions/categories.html")

def watchlist(request):
    return render(request, "auctions/watchlist.html")
