from django.db.models import Avg, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from game.models import Game, GameOrder
from .models import Basket, Wishlist

def calculate_basket_price(basket, context):
    full_price = 0
    final_price = 0
    for game in basket.games.all():
        full_price += game.price
        final_price += (game.price - game.discount_amount)
    discount = full_price - final_price
    context["full_price"] = full_price
    context["discount"] = discount
    context["final_price"] = final_price
    return context

def get_top_rated_games():
    MINIMUM_REVIEWS = 5
    MEAN_RATING = 3

    top_rated = Game.objects.annotate(
        avg_rating=Coalesce(Avg('reviews__rating', output_field=FloatField()), 0),
        review_count=Count('reviews'),
    ).annotate(
        weighted_score=ExpressionWrapper(
            (F('review_count') * F('avg_rating') + MINIMUM_REVIEWS * MEAN_RATING) /
            (F('review_count') + MINIMUM_REVIEWS),
            output_field=FloatField()
        )
    ).order_by('-weighted_score')[:10]

    return top_rated

class GameRecommendation:
    def __init__(self, user:User):
        self.user = user
    
    def get_frequently_bought_together(self, game:Game, limit:int=6):
        games = Game.objects.filter(gameorder__status=2, gameorder__games=game).exclude(id=game.id).distinct()[:limit]
        if not games:
            return self.get_similar_genre_games(game=game, limit=limit)
    
    def get_similar_genre_games(self, game:Game, limit:int=6):
        genres = game.genre.all()
        games = Game.objects.filter(genre__in=genres).exclude(id=game.id).distinct()[:limit]
        if not games:
            return Game.objects.exclude(id=game.id)[:6]
        else:
            return games
