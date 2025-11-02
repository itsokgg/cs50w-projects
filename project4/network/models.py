from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    user_followers = models.ManyToManyField('Follow')

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=256, blank=False, null=False)
    likes = models.ManyToManyField(User, through="Like", blank=True, related_name="liked_posts")
    timestamp = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')

class Follow(models.Model):
    # user who is being followed
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    # user who is following the followed user
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followings")

    class Meta:
        unique_together = ('followed', 'following')