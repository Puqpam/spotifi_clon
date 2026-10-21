from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from mutagen import File as MutagenFile

from music.models import Artist, Track


class Command(BaseCommand):
    help = "Импортирует все mp3 из указанной папки"

    def add_arguments(self, parser):
        parser.add_argument("folder", type=str)

    def handle(self, *args, **options):
        folder = Path(options["folder"])
        if not folder.is_dir():
            self.stderr.write("Папка не найдена")
            return

        for path in sorted(folder.glob("*.mp3")):
            title = path.stem
            artist_name = "Unknown Artist"
            duration = 0

            audio = MutagenFile(path, easy=True)
            if audio is not None:
                tags = audio.tags or {}
                title = (tags.get("title") or [title])[0]
                artist_name = (tags.get("artist") or [artist_name])[0]
                duration = int(audio.info.length)

            artist, _ = Artist.objects.get_or_create(name=artist_name)

            if Track.objects.filter(title=title, artist=artist).exists():
                self.stdout.write(f"Пропущен (уже есть): {artist} - {title}")
                continue

            with open(path, "rb") as f:
                track = Track(title=title, artist=artist, duration=duration)
                track.audio_file.save(path.name, File(f), save=True)

            self.stdout.write(f"Добавлен: {artist} - {title}")