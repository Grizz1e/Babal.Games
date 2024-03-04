from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
import uuid


# Create your models here.
def banner_upload(instance, filename):
    return f'banner/{uuid.uuid4()}.{filename.split(".")[-1]}'

def screenshot_upload(instance, filename):
    return f'screenshots/{uuid.uuid4()}.{filename.split(".")[-1]}'

class Game(models.Model):
    display_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=50)
    description = models.TextField(max_length=500, blank=True)

    user_rating = models.FloatField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ])

    banner = models.ImageField(upload_to=banner_upload)

    price = models.FloatField(default=0)
    discount_amount = models.FloatField(default=0)

    copies_sold = models.IntegerField(default=0)

    is_available_on_windows = models.BooleanField(default=False)
    is_available_on_linux = models.BooleanField(default=False)
    is_available_on_mac = models.BooleanField(default=False)

    def __str__(self):
        return self.display_name

class GameRating(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE)

    five_stars = models.IntegerField(default=0)
    four_stars = models.IntegerField(default=0)
    three_stars = models.IntegerField(default=0)
    two_stars = models.IntegerField(default=0)
    one_stars = models.IntegerField(default=0)

    def __str__(self):
        return self.game.display_name
    
class GameReview(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    review = models.TextField(max_length=500, blank=True)
    rating = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])

    def __str__(self):
        return self.reviewer.username + " - " + self.game.slug


class GameCode(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True)
    
    is_sold = models.BooleanField(default=False)
    sold_to = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    date_added = models.DateTimeField(default=timezone.now)
    date_sold = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.game.slug + " - " + self.code
    
class GameScreenshot(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=screenshot_upload)

    def __str__(self):
        return self.game.display_name
    


class Basket(models.Model):
    games = models.ManyToManyField(Game, blank=True)
    buyer = models.OneToOneField(User, on_delete=models.CASCADE)
    total_price = models.FloatField(default=0, validators=[
        MinValueValidator(0)
    ])

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
    

class GameOrder(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4().hex, editable=False, null=True, blank=True)
    buyer = models.OneToOneField(User, on_delete=models.CASCADE)
    games = models.ManyToManyField(Game, blank=True)
    total_price = models.FloatField(default=0, validators=[
        MinValueValidator(10)
    ])

    is_payment_successful = models.BooleanField(default=False)

    def __str__(self):
        return self.buyer.username + " " + str(self.order_id)


@receiver(models.signals.post_save, sender=Game)
def create_game_related_data(sender, instance, created, **kwargs):
    if created:
        GameRating.objects.create(game=instance)

@receiver(models.signals.post_save, sender=User)
def created_user_related_data(sender, instance, created, **kwargs):
    if created:
        Basket.objects.create(buyer=instance)
        Wishlist.objects.create(buyer=instance)