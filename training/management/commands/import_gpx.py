from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from training.models import Workout, Sample
import gpxpy
from pathlib import Path

def extract_hr_from_extensions(pt):
    try:
        for ext in getattr(pt, "extensions", []) or []:
            for elem in ext.iter():
                tag = elem.tag.split('}')[-1].lower()
                if tag == 'hr' and elem.text:
                    s = ''.join(ch for ch in elem.text if ch.isdigit())
                    if s:
                        return int(s)
    except Exception:
        pass
    return None

class Command(BaseCommand):
    help = "Import GPX z próbkami HR"

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("gpx_path")

    def handle(self, *args, **opts):
        user = User.objects.get(username=opts["username"])
        p = Path(opts["gpx_path"])
        if not p.exists():
            raise CommandError(f"Nie znaleziono pliku: {p}")

        with p.open("r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)

        points = []
        for trk in gpx.tracks:
            for seg in trk.segments:
                for pt in seg.points:
                    hr = extract_hr_from_extensions(pt)
                    points.append((pt.time, hr))

        if not points:
            raise CommandError("Brak punktów w GPX")

        start = points[0][0]
        end = points[-1][0]
        duration_s = int((end - start).total_seconds())

        w = Workout.objects.create(
            user=user, date=start, duration_s=duration_s, distance_m=0, source='gpx'
        )
        Sample.objects.bulk_create([Sample(workout=w, t=t, hr=hr) for (t, hr) in points])

        hrs = [hr for (_, hr) in points if hr is not None]
        if hrs:
            w.avg_hr = sum(hrs) // len(hrs)
            w.max_hr = max(hrs)
            w.save()

        self.stdout.write(self.style.SUCCESS(
            f"Zaimportowano trening ID={w.id} (HRavg={w.avg_hr}, HRmax={w.max_hr})"
        ))