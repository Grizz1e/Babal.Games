from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import models
from account.models import UserProfile
from game.models import Game

# Create your models here.
class Basket(models.Model):
    games = models.ManyToManyField(Game, blank=True)
    buyer = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.buyer.username
    
class Wishlist(models.Model):
    games = models.ManyToManyField(Game, blank=True)
    buyer = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.buyer.username
    
class FeaturedGame(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE, unique=True)
    tag = models.CharField(max_length=50)
    tag_color_code = models.CharField(max_length=7)

    def __str__(self):
        return self.game.display_name
    
@receiver(models.signals.post_save, sender=User)
def created_user_related_data(sender, instance, created, **kwargs):
    if created:
        Basket.objects.create(buyer=instance)
        Wishlist.objects.create(buyer=instance)
        UserProfile.objects.create(user=instance)