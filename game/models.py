from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
import uuid, os
from django.core.files.storage import FileSystemStorage
from django.conf import settings

class OutsideMediaStorage(FileSystemStorage):
    def __init__(self, location=None):
        # Set your custom location outside MEDIA_ROOT here
        if location is None:
            location = os.path.join('game_builds')
        super().__init__(location=location)


# Create your models here.
def banner_upload(instance, filename):
    return f'banner/{uuid.uuid4()}.{filename.split(".")[-1]}'

def screenshot_upload(instance, filename):
    return f'screenshots/{uuid.uuid4()}.{filename.split(".")[-1]}'

def game_build_upload(instance, filename):
    return f'{uuid.uuid4()}.{filename.split(".")[-1]}'

def unique_order_id():
    return uuid.uuid4()

class NewGameGenre(models.Model):
    display_name = models.CharField(max_length=100)
    slug = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.display_name

class Game(models.Model):
    display_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=50)
    description = models.TextField(max_length=500, blank=True)
    long_description = models.TextField(default="No description provided", blank=True)
    genre = models.ManyToManyField(NewGameGenre, blank=True)

    banner = models.ImageField(upload_to=banner_upload)
    yt_trailer_id = models.CharField(verbose_name="YouTube trailer ID", max_length=20, blank=True)
    steam_id = models.CharField(verbose_name="Steam App ID", max_length=10, blank=True)

    licensed_to = models.ManyToManyField(verbose_name="Licensed To", to=User, blank=True)

    price = models.FloatField(default=0)
    discount_amount = models.FloatField(default=0)

    is_available_on_windows = models.BooleanField(default=False)
    is_available_on_linux = models.BooleanField(default=False)
    is_available_on_mac = models.BooleanField(default=False)

    developer = models.CharField(max_length=100, blank=True, null=True)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    support_url = models.CharField(max_length=250, blank=True, null=True)

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
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField(max_length=500, blank=True)
    rating = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])
    review_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.reviewer.username + " - " + self.game.slug


class GameCode(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True)
    
    is_sold = models.BooleanField(default=False)
    sold_to = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    associated_order_id = models.UUIDField(blank=True, null=True)

    date_added = models.DateTimeField(default=timezone.now)
    date_sold = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.game.slug + " - " + self.code
    
class GameScreenshot(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=screenshot_upload)

    def __str__(self):
        return self.game.display_name
    


class GameVoucher(models.Model):
    voucher_code = models.CharField(max_length=20, unique=True)
    used_by = models.ManyToManyField(User, blank=True)
    # create voucher type choice field
    class VoucherType(models.TextChoices):
        PERCENTAGE = "percentage"
        AMOUNT = "amount"
    voucher_type = models.CharField(max_length=10, choices=VoucherType.choices, default=VoucherType.PERCENTAGE)
    minimum_spend = models.FloatField(default=0)
    max_discount_amount = models.FloatField()
    percentage_discount = models.FloatField(validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])

    def __str__(self):
        return self.voucher_code

class GameBuild(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE)
    zip_file = models.FileField(upload_to=game_build_upload, storage=OutsideMediaStorage)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id}"

class GameOrder(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    games = models.ManyToManyField(Game, blank=True)
    total_price = models.FloatField(default=0, validators=[
        MinValueValidator(10)
    ])
    voucher = models.OneToOneField(GameVoucher, blank=True, null=True, on_delete=models.SET_NULL)
    voucher_amount = models.FloatField(default=0)

    STATUS_CHOICES =( 
        (1, "Pending"),
        (2, "Completed"),
        (3, "Cancelled"),
        (4, "Expired"),
        (5, "Failed"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES)

    is_payment_successful = models.BooleanField(default=False)
    order_date = models.DateTimeField(default=timezone.now)
    pidx = models.CharField(max_length=100, blank=True)

    def is_expired(self):
        """Check if the order should be marked as expired."""
        if self.status == 1:  # Pending
            expiration_time = self.order_date + timezone.timedelta(minutes=30)
            return timezone.now() > expiration_time
        return False

    def __str__(self):
        return self.buyer.username + " " + str(self.order_id)
    
class RecommendedSystemRequirement(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    os = models.CharField(max_length=250)
    processor = models.CharField(max_length=500)
    memory = models.CharField(max_length=250)
    graphics = models.CharField(max_length=250)
    storage = models.CharField(max_length=250)
    additional_note = models.TextField(max_length=1000, blank=True)

class MinSystemRequirement(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    os = models.CharField(max_length=250)
    processor = models.CharField(max_length=500)
    memory = models.CharField(max_length=250)
    graphics = models.CharField(max_length=250)
    storage = models.CharField(max_length=250)
    additional_note = models.TextField(max_length=1000, blank=True)


@receiver(models.signals.post_save, sender=Game)
def create_game_related_data(sender, instance, created, **kwargs):
    if created:
        GameRating.objects.create(game=instance)
