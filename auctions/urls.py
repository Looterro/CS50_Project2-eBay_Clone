from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("create_listing", views.create_listing, name="create_listing"),
#    path("listing", views.listing, name="listing"),
#    path("listing/<str:id>/comment", views.listing_comment, name="listing_comment"),
#    path("listing/<str:id>/close", views.listing_close, name="close_listing"),
#    path("listing/<str:id>/watch", views.watch, name="add_to_watchlist"),
]
