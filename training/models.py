from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()
    duration_s = models.IntegerField()
    distance_m = models.IntegerField(default=0)
    avg_hr = models.IntegerField(null=True, blank=True)
    max_hr = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=20, default='gpx')

class Sample(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='samples')
    t = models.DateTimeField()
    hr = models.IntegerField(null=True, blank=True)
