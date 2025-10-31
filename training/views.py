from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from .models import Workout

def workout_list(request):
    workouts = Workout.objects.order_by('-date')[:50]
    return render(request, 'training/workout_list.html', {'workouts': workouts})

def workout_detail(request, pk):
    w = get_object_or_404(Workout, pk=pk)
    samples = w.samples.order_by('t').values_list('t','hr')
    data = [{'t': t.isoformat(), 'hr': hr} for (t, hr) in samples if hr is not None]
    return render(request, 'training/workout_detail.html', {'w': w, 'data': data})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import import_gpx_for_user

@login_required(login_url='/admin/login/')
def upload_gpx(request):
    if request.method == 'POST':
        f = request.FILES.get('gpx_file')
        if not f:
            messages.error(request, "Wybierz plik .gpx")
            return redirect('upload_gpx')
        try:
            w = import_gpx_for_user(request.user, f)
            messages.success(request, f"Zaimportowano trening ID={w.id} (HRavg={w.avg_hr}, HRmax={w.max_hr})")
            return redirect('workout_detail', pk=w.id)
        except Exception as e:
            messages.error(request, f"Błąd importu: {e}")
            return redirect('upload_gpx')

    return render(request, 'training/upload_gpx.html')