from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    users = models.OneToOneField(User, on_delete=models.CASCADE)
    banned = models.BooleanField(default=False)
    user_points = models.IntegerField(default=0)
    last_answer_time = models.IntegerField(default=0)
    num_completed_levels = models.IntegerField(default=0)