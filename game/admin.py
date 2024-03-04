from django.contrib import admin
from .models import Game, GameRating, GameReview, GameCode, GameScreenshot, Basket, Wishlist, FeaturedGame, GameOrder

# Register your models here.
admin.site.register(Game)
admin.site.register(GameRating)
admin.site.register(GameReview)
admin.site.register(GameCode)
admin.site.register(GameScreenshot)
admin.site.register(Basket)
admin.site.register(Wishlist)
admin.site.register(FeaturedGame)
admin.site.register(GameOrder)