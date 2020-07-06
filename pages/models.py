from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    banned = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    current_level = models.IntegerField(default=0)
