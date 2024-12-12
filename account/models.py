from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from game.models import Game
from random import randrange
# Create your models here.

def avatar_upload(instance, filename):
    return f'avatar/{filename.split(".")[0]}.{filename.split(".")[-1]}'

def set_random_avatar():
    return randrange(6) + 1

class ProfileAvatar(models.Model):
    avatar = models.ImageField(upload_to=avatar_upload)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.game.display_name
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar_id = models.IntegerField(default=set_random_avatar)
    def __str__(self):
        return self.user.username