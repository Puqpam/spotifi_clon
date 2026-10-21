from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Artist, Like, Playlist, PlaylistTrack, Subscription, Track


def _context(request, tracks, title, active, q="", playlist=None):
    liked_ids, sub_ids, playlists = set(), set(), []
    if request.user.is_authenticated:
        liked_ids = set(Like.objects.filter(user=request.user).values_list("track_id", flat=True))
        sub_ids = set(Subscription.objects.filter(user=request.user).values_list("artist_id", flat=True))
        playlists = Playlist.objects.filter(owner=request.user)
    return {
        "tracks": tracks,
        "page_title": title,
        "active": active,
        "q": q,
        "liked_ids": liked_ids,
        "sub_ids": sub_ids,
        "playlists": playlists,
        "current_playlist": playlist,
    }


def track_list(request):
    q = request.GET.get("q", "").strip()
    tracks = Track.objects.select_related("artist", "album")
    if q:
        tracks = tracks.filter(Q(title__icontains=q) | Q(artist__name__icontains=q))
        title = f"Результаты по запросу «{q}»"
    else:
        title = "Все треки"
    return render(request, "music/track_list.html", _context(request, tracks, title, "home", q))


@login_required
def liked_tracks(request):
    tracks = Track.objects.filter(like__user=request.user).select_related("artist", "album")
    return render(request, "music/track_list.html", _context(request, tracks, "Любимые треки", "liked"))


@login_required
def subscriptions(request):
    tracks = Track.objects.filter(artist__subscribers__user=request.user).select_related("artist", "album")
    return render(request, "music/track_list.html", _context(request, tracks, "Треки ваших подписок", "subs"))


@login_required
@require_POST
def create_playlist(request):
    title = request.POST.get("title", "").strip()
    if not title:
        return redirect("track_list")
    playlist = Playlist.objects.create(owner=request.user, title=title)
    return redirect("playlist_detail", pk=playlist.pk)


@login_required
def playlist_detail(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk, owner=request.user)
    tracks = (
        Track.objects.filter(playlisttrack__playlist=playlist)
        .select_related("artist", "album")
        .order_by("playlisttrack__position")
    )
    return render(
        request,
        "music/track_list.html",
        _context(request, tracks, playlist.title, "playlist", playlist=playlist),
    )


@require_POST
def add_to_playlist(request, pk, track_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "auth"}, status=401)
    playlist = get_object_or_404(Playlist, pk=pk, owner=request.user)
    track = get_object_or_404(Track, id=track_id)
    if PlaylistTrack.objects.filter(playlist=playlist, track=track).exists():
        return JsonResponse({"added": False})
    position = PlaylistTrack.objects.filter(playlist=playlist).count() + 1
    PlaylistTrack.objects.create(playlist=playlist, track=track, position=position)
    return JsonResponse({"added": True})


@require_POST
def toggle_like(request, track_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "auth"}, status=401)
    track = get_object_or_404(Track, id=track_id)
    like, created = Like.objects.get_or_create(user=request.user, track=track)
    if not created:
        like.delete()
    return JsonResponse({"liked": created})


@require_POST
def toggle_subscribe(request, artist_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "auth"}, status=401)
    artist = get_object_or_404(Artist, id=artist_id)
    sub, created = Subscription.objects.get_or_create(user=request.user, artist=artist)
    if not created:
        sub.delete()
    return JsonResponse({"subscribed": created})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("track_list")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})