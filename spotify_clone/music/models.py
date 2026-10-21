from django.db import models
from django.contrib.auth.models import User


class Artist(models.Model):
    name = models.CharField(max_length=200)
    avatar = models.ImageField(upload_to="artists/", blank=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="albums")
    cover = models.ImageField(upload_to="covers/", blank=True)
    release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"


class Track(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="tracks")
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True, related_name="tracks")
    audio_file = models.FileField(upload_to="tracks/")
    duration = models.PositiveIntegerField(default=0)  # секунды
    play_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.artist}"


class Playlist(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="playlists")
    title = models.CharField(max_length=200)
    is_public = models.BooleanField(default=False)
    tracks = models.ManyToManyField(Track, through="PlaylistTrack")

    def __str__(self):
        return self.title


class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ["position"]


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "track")


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="subscribers")

    class Meta:
        unique_together = ("user", "artist")