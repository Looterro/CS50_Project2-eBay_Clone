from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import User, Listing, Bid, Category, Comment
from django.forms import ModelForm

"""
Forms:
"""

# Form for placing bids:
class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
    
    def __init__(self, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control m-2'

# Form for creating new listings:
class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['item_name', 'picture', 'item_description', 'initial_bid', 'listing_duration', 'category']
    
    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

# Form for submitting comments:
class CommentForm(ModelForm):
    
    class Meta:
        model = Comment
        fields = ['message']
    
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['style'] = 'border: none; box-shadow: 5px 6px 6px 2px #e9ecef; border-radius 4px; height:150px'

"""
Views:
"""
# Renders a list of all active auctions:
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
        return render(request, "auctions/listing.html", context)
    
    # Calculate remaining time:
    time_remaining = listing.end_time - timezone.now()
    context["days"] = time_remaining.days
    context["hours"] = int(time_remaining.seconds/3600)
    context["minutes"] = int(time_remaining.seconds/60 - (context["hours"] * 60))
    context["bid_form"] = BidForm()
    context["comment_form"] = CommentForm()

    return render(request, "auctions/listing.html", context)

# Renders page with new auction listing form:
def create_listing(request):
    form = ListingForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        new_listing = form.save(commit = False)
        new_listing.user = request.user
        new_listing.save()
        return HttpResponseRedirect(reverse('listing', kwargs={"id": new_listing.id}))
    else:
        return render(request, "auctions/create_listing.html", {
            'form': form
        })

# Action after clicking the button for ending auction early, redirects to the same listing:
def listing_close(request, id):
    listing = Listing.objects.get(id=id)
    if request.user == listing.user:
        listing.ended_manually = True
        listing.save()
    
    return HttpResponseRedirect(reverse('listing', kwargs={"id": id}))

# Adds or removes listing to user's watchlist after clicking the watchlist button: 
def toggle_watchlist(request, id):
    if request.method == "POST":
        listing = Listing.objects.get(id=id)
        watchlist = request.user.watchlist
        if listing in watchlist.all():
            watchlist.remove(listing)
        else:
            watchlist.add(listing)
    
    return HttpResponseRedirect(reverse('listing', kwargs={"id":id}))

# Places the bid after submitting the value and returns to the same listing with updated data:
def bid(request, id):
    bid_form = BidForm(request.POST or None)
    
    if bid_form.is_valid():
        listing = Listing.objects.get(id=id)
        user = request.user
        new_bid = bid_form.save(commit=False)
        existing_bids = Bid.objects.filter(listing=listing)
        highest_bid_check = all(new_bid.amount > n.amount for n in existing_bids)
        not_highest = new_bid.amount >= listing.initial_bid

        if highest_bid_check and not_highest:
            new_bid.listing = listing
            new_bid.user = request.user
            new_bid.save()
    
    return HttpResponseRedirect(reverse('listing', kwargs={'id': id}))

# Filters listings by category and displays category in category view page:
def category(request, name):
    category = Category.objects.get(name=name)
    listings = Listing.object.filter(category = category, ended_manually = False, end_time__gte=datetime.now())
    
    return render(request, "listings/category.html", {
        "listings": listings,
        "title": category.name,
        "category": category.name
    })

# Action after submitting the comment:
def listing_comment(request, id):
    comment_form = CommentForm(request.POST or None)

    #add comment to database:
    if comment_form.is_valid():
        new_comment = comment_form.save(commit=False)
        new_comment.listing = Listing.objects.get(id=id)
        new_comment.user = request.user
        new_comment.save()

    return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))

def categories(request):
    return render(request, "auctions/categories.html")

def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all(),
        "title": "Your Watchlist"
    })
# Action after clicking the button for submitting the comment and saving it:
def auction_comment(request, id):
    comment_form = CommentForm(request.POST or None)

    # Add comment to database:
    if comment_form.is_valid():
        new_comment = comment_form.save(commit=False)
        new_comment.listing = Listing.objects.get(id=id)
        new_comment.user = request.user
        new_comment.save()
    
    return HttpResponseRedirect(reverse('auction', kwargs={"id": id}))
    