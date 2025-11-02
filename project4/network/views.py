import json
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt


from .models import User, Post, Like, Follow

def index(request):
    posts = Post.objects.order_by('-timestamp').values()
    if request.user.is_authenticated:
        for post in posts:
            
            post["user"] = User.objects.get(pk=post.get("user_id")).username
            post["likes"] = Post.objects.get(pk=post.get("id")).likes.count()
            
            # check if user liked this post
            post_object = Post.objects.get(pk=post["id"])
            try:
                like = Like.objects.get(
                    user=request.user,
                    post=post_object
                )
            except Like.DoesNotExist:
                post["liked"] = False
            else:
                post["liked"] = True
    else:
        for post in posts:
            post["user"] = User.objects.get(pk=post.get("user_id")).username
            post["likes"] = Post.objects.get(pk=post.get("id")).likes.count()
    
    # make pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page": page_obj
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

@login_required()
def post(request):
    try:
        post = Post(
            user=request.user,
            text=request.POST.get("text")
        )
    
    except ValidationError:
        return HttpResponseBadRequest({f"{errror}"})

    post.save()
    
    return HttpResponseRedirect(reverse("index"))

def profile(request, username):
    user_profile = User.objects.get(username=username)
    current_user = request.user
    user_posts = Post.objects.filter(user=user_profile).order_by('-timestamp')
    followers = user_profile.followers.all()
    following_count = user_profile.followings.count()
    
    # check if user is logged in and is following
    if (current_user) and (current_user != user_profile):
        follow_status = False
        for follower in followers:
            if current_user.id == follower.following_id:
                follow_status = "following"
                break
        if not follow_status:
            follow_status ="not_following"
    else:
        follow_status = False

    l = []
    for post in user_posts:
        
        d = {
            "id": post.id,
            "user_id": post.user_id,
            "text": post.text,
            "timestamp": post.timestamp,
            "likes": post.likes.count()
        }

        # check if user liked this post
        post_object = Post.objects.get(pk=post.id)
        try:
            like = Like.objects.get(
                user=request.user,
                post=post_object
            )
        except Like.DoesNotExist:
            d["liked"] = False
        else:
            d["liked"] = True
        
        l.append(d)

    # make pagination
    paginator = Paginator(l, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/profile.html", {
        "username": username, # dont pass user as key to template or django will say the value is the user
        "follows": len(followers),
        "following": following_count,
        "follow_status": follow_status,
        "page": page_obj
    })
    
@login_required()
def follow(request):
    if request.method == "POST":
        action = request.POST.get("action")
        username = request.POST.get("username")
        if action == "follow":
            follow = Follow(
                followed=User.objects.get(username=username),
                following=request.user
            )
            follow.save()
        else: # action == "unfollow"
            follow = Follow.objects.get(followed=User.objects.get(username=username), following=request.user)
            follow.delete()
        return HttpResponseRedirect(reverse("profile", kwargs={"username":username}))

@login_required()
def following(request):
    # get the users followings
    followings = request.user.followings.values('followed')
    # get followings' posts
    posts = Post.objects.filter(user__in=followings).order_by('-timestamp').values()
    for post in posts:
        post["user"] = User.objects.get(pk=post.get("user_id")).username
        post["likes"] = Post.objects.get(pk=post.get("id")).likes.count()
        
        # check if user liked this post
        post_id = Post.objects.get(pk=post["id"])
        try:
            like = Like.objects.get(
                user=request.user,
                post=post_id
            )
        except Like.DoesNotExist:
            post["liked"] = False
        else:
            post["liked"] = True
    
    # make pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page": page_obj
    })

@csrf_exempt
@login_required()
def edit(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        post = Post.objects.get(pk=data["post"])
        
        # editer must be poster
        if request.user != post.user:
            return HttpResponseBadRequest("You cannot edit this post!")
        
        post.text = data["text"]
        post.save()

        return HttpResponse(status=204)

@csrf_exempt
@login_required()
def like(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        post = Post.objects.get(pk=data["post"])
        
        if data["action"] == 'like':
            try:
                like = Like(
                    user=request.user,
                    post=post
                )
                like.save()
            except IntegrityError:
                #return HttpResponseBadRequest("You can only like a post once!")
                pass
        
        elif data["action"] == "unlike":
            like = Like.objects.get(
                user=request.user,
                post=post
            )
            like.delete()

        return HttpResponse(status=204)