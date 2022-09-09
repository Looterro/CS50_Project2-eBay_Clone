from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    def __str__(self):
       return f"{self.username}"

class Category(models.Model):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    item_name = models.TextField(max_length = 256)
    item_description = models.TextField(max_length=512)
    picture = models.ImageField(blank = True, null = True, upload_to='', default = 'default.jpg')
    initial_bid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    category = models.ForeignKey(Category, blank = True, null = True, on_delete = models.SET_NULL, related_name='listings')
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    ended_manually = models.BooleanField(default = False)
    listing_duration = models.IntegerField(choices=((1, "One Day"), (3, "Three Days"), (7, "One week")))

    submit_bid = models.DecimalField(max_digits = 10, decimal_places = 2, validators = [MinValueValidator(0.01)])

    def __str__(self):
        return f"Listing #{self.id}: {self.item_name} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(days=self.listing_duration)
        super().save(*args, **kwargs)
    
    def is_finished(self):
        if self.ended_manually or self.end_time < timezone.now():
            return True
        else:
            return False

"""
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    message = models.TextField(max_length = 256)
    time = models.DateTimeField(auto_now_add=True)
"""

class Bid(models.Model):
    amount = models.DecimalField(max_digits= 10, decimal_places= 2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

def __str__(self):
    return f"Bid #{self.id}: {self.amount} on {self.listing.item_name} by {self.username}"