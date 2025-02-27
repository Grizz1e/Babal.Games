from .models import Game, GameRating, \
    GameReview, GameCode, GameScreenshot, \
    GameOrder, GameVoucher, NewGameGenre, \
    MinSystemRequirement, RecommendedSystemRequirement, \
    GameBuild
from django.contrib import admin

# Register your models here.
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'price', 'discount_amount', 'is_available_on_windows', 'is_available_on_linux', 'is_available_on_mac']

@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    list_display = ['game', 'five_stars', 'four_stars', 'three_stars', 'two_stars', 'one_stars']

@admin.register(GameReview)
class GameReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'game', 'review', 'rating']

@admin.register(GameCode)
class GameCodeAdmin(admin.ModelAdmin):
    list_display = ['game', 'code', 'is_sold', 'date_added']

@admin.register(GameScreenshot)
class GameScreenshotAdmin(admin.ModelAdmin):
    list_display = ['game', 'image']

@admin.register(GameOrder)
class GameOrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'buyer', 'total_price', 'is_payment_successful', 'order_date']

@admin.register(NewGameGenre)
class NewGameGenreAdmin(admin.ModelAdmin):
    list_display = ["display_name"]

@admin.register(MinSystemRequirement)
class MinSystemRequirementAdmin(admin.ModelAdmin):
    list_display = ["game"]

@admin.register(RecommendedSystemRequirement)
class RecommendedSystemRequirementAdmin(admin.ModelAdmin):
    list_display = ["game"]

@admin.register(GameBuild)
class GameBuildAdmin(admin.ModelAdmin):
    list_display = ["game", "id"]
    
admin.site.register(GameVoucher)