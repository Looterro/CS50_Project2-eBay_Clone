from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    name = models.TextField(max_length = 256)
    picture = models.TextField(max_length = 256)
    price = models.TextField(max_length = 16)
    bids = models.TextField
    category = models.TextField
    watchlist = models.TextField

class Auction(models.Model):
    pass

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="auctions")
    message = models.TextField(max_length = 256)
    time = models.DateTimeField(auto_now_add=True)