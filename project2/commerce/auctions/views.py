from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .models import User, AuctionListing, Bid, Comment, Watchlist
from . import util

def index(request):
    listings = AuctionListing.objects.all()
    listings_final = []
    for listing in listings:
        listings_final.append(util.get_listing_info(listing))
        
    return render(request, "auctions/index.html", {
        "listings": listings_final
    })


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

@login_required()
def create_listing(request):
    if request.method == "POST":
        if not request.POST.get("title") or not request.POST.get("description") or not request.POST.get("starting_bid"):
            return HttpResponseBadRequest("Information is not valid")
        try:
            listing = AuctionListing(
                seller_user_id=request.user,
                title=request.POST.get("title"),
                description=request.POST.get("description"),
                starting_bid=request.POST.get("starting_bid"),
                image_url=request.POST.get("img"),
                category=request.POST.get("category").strip().capitalize()
            )
            listing.save()
        except (ValueError, ValidationError):
            return HttpResponseBadRequest("Information is not valid")

        return  HttpResponseRedirect(reverse("index"))

    categories = ["Furniture", "fashion", "Electronics", "Toys", "Office", "Home", "All Other"]
    return render(request, "auctions/create-listing.html", {
        "categories": categories
    })

def view_listing(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    listing_info = util.get_listing_info(listing)
    comments = Comment.objects.filter(auction_id=listing)
    try:
        watchlist = Watchlist.objects.get(user_id=request.user, auction_id=listing_id)
    #if not in wishlist or user not logged in
    except (Watchlist.DoesNotExist, TypeError):  
        watchlist = False
    
    if request.user == listing.seller_user_id:
        lister = True
    else:
        lister = False

    return render(request, "auctions/view-listing.html", {
        "listing": listing_info,
        "watchlist": watchlist,
        "comments": comments,
        "lister": lister
        })

@login_required()
def watchlist(request):
    if request.method == "POST":
        listing = AuctionListing.objects.get(pk=int(request.POST.get("listing")))
        if request.POST.get("add"):
            try:
                watchlist = Watchlist(
                    user_id=request.user,
                    auction_id=listing
                )
                watchlist.save()
            except (ValueError, ValidationError) as error:
                return HttpResponseBadRequest(f"Information is not valid! {error}\
                listing: {listing} user: {request.user}")
        # if request.POST.get("remove")
        else:
            try:
               Watchlist.objects.filter(
                user_id=request.user, 
                auction_id=listing
            ).delete()
            except FieldError:
                return HttpResponseBadRequest("Information is not valid")

    watchlist = Watchlist.objects.filter(user_id=request.user)
    listings = []
    for item in watchlist:
        listings.append(AuctionListing.objects.get(pk=item.auction_id.pk))
    return render(request, "auctions/watchlist.html", {
        "watchlist": listings
    })


@login_required()
def place_bid(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    listing_info = util.get_listing_info(listing)
    
    try:
        if int(request.POST.get("bid")) < int(listing_info.get("starting_bid")):
            return HttpResponseBadRequest(f"starting bid is: {listing_info.get("starting_bid")}")
    except TypeError:
        if int(request.POST.get("bid")) <= int(listing_info.get("bid")):
            return HttpResponseBadRequest(f"you must bid over: {listing_info.get("bid")}")
        
    try:
        bid = Bid(
            auction_id=listing,
            bidder_user_id=request.user,
            amount=request.POST.get("bid")
        )
        bid.save()
    except (ValueError, ValidationError) as error:
        return HttpResponseBadRequest(f"Information is not valid, error: {error}")
    
    return HttpResponseRedirect(reverse("view-listing", kwargs={"listing_id":listing_id}))
        

@login_required()
def comment(request, listing_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(pk=listing_id)
        try:
            comment = Comment(
            auction_id=listing,
            commenter_user_id=request.user,
            comment=request.POST.get("comment")
            )
            comment.save()
        except (ValueError, ValidationError) as error:
            return HttpResponseBadRequest(f"Information is not valid, error: {error}")
    
    return HttpResponseRedirect(reverse("view-listing", kwargs={"listing_id":listing_id}))

@login_required()
def close_listing(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    if request.user == listing.seller_user_id:
        listing.active = False
        listing.save()
    else:
        return HttpResponseBadRequest(f"You cannot close a listing you didn't list!")

    return HttpResponseRedirect(reverse("view-listing", kwargs={"listing_id":listing_id}))

def category_view(request):
    if request.method == "POST":
        listings = AuctionListing.objects.filter(category=request.POST.get("category").strip().capitalize())
        
        listings_final = []
        for listing in listings:
            listings_final.append(util.get_listing_info(listing))
        
        return render(request, "auctions/category-view.html", {
            "listings": listings_final
        })
    
    categories = ["Furniture", "fashion", "Electronics", "Toys", "Office", "Home", "All Other"]

    return render(request, "auctions/category-search.html", {
        "categories": categories
    })