from pathlib import Path
import gpxpy
from .models import Workout, Sample

def _extract_hr(pt):
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

def import_gpx_for_user(user, file_obj):
    """
    Przyjmuje plik/plikopodobny obiekt GPX (np. request.FILES['gpx_file']).
    Zwraca utworzony Workout.
    """
    gpx = gpxpy.parse(file_obj)

    points = []
    for trk in gpx.tracks:
        for seg in trk.segments:
            for pt in seg.points:
                hr = _extract_hr(pt)
                points.append((pt.time, hr))

    if not points:
        raise ValueError("Brak punktów w GPX (nie znaleziono próbek)")

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

    return w