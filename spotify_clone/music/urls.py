from django.urls import path
from . import views

urlpatterns = [
    path("", views.track_list, name="track_list"),
    path("register/", views.register, name="register"),
    path("liked/", views.liked_tracks, name="liked"),
    path("subscriptions/", views.subscriptions, name="subscriptions"),
    path("like/<int:track_id>/", views.toggle_like, name="toggle_like"),
    path("subscribe/<int:artist_id>/", views.toggle_subscribe, name="toggle_subscribe"),
    path("playlist/create/", views.create_playlist, name="create_playlist"),
    path("playlist/<int:pk>/", views.playlist_detail, name="playlist_detail"),
    path("playlist/<int:pk>/add/<int:track_id>/", views.add_to_playlist, name="add_to_playlist"),
]