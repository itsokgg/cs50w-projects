from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.create_listing, name="create-listing"),
    path("view-listing/<int:listing_id>", views.view_listing, name="view-listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("place_bid/<int:listing_id>", views.place_bid, name="place-bid"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("close-listing/<int:listing_id>", views.close_listing, name="close-listing"),
    path("category-view", views.category_view, name="view-listing-by-category")
]
