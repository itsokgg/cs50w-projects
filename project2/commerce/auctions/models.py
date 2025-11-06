import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    seller_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    title = models.CharField(max_length=64, blank=False, null=False)
    description = models.CharField(max_length=512, blank=False, null=False)
    starting_bid = models.IntegerField(blank=False, null=False)
    image_url = models.CharField(max_length=256, blank=True, null=True)
    category = models.CharField(max_length=64, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)
    bidders = models.ManyToManyField(User, through="Bid", blank=True, related_name="bidded_auctions")
    
class Bid(models.Model):
    auction_id = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    bidder_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    

class Comment(models.Model):
    auction_id = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    commenter_user_id = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.CharField(max_length=512)
    date = models.DateField(auto_now_add=True)

class Watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_id = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user_id', 'auction_id')
