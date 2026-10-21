from django.contrib import admin
from .models import Artist, Album, Track, Playlist, PlaylistTrack, Like

admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Track)
admin.site.register(Playlist)
admin.site.register(PlaylistTrack)
admin.site.register(Like)