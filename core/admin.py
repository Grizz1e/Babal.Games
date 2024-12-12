from .models import Basket, Wishlist, FeaturedGame
from django.contrib import admin

# Register your models here.
@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['buyer']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['buyer']

@admin.register(FeaturedGame)
class FeaturedGameAdmin(admin.ModelAdmin):
    list_display = ['game', 'tag', 'tag_color_code']