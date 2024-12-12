from game.models import Game, GameGenre, GameOrder, GameRating, GameReview, GameScreenshot
from django.contrib.auth.decorators import login_required
from account.models import UserProfile, ProfileAvatar
from .models import Basket, Wishlist, FeaturedGame
from core.utils import calculate_basket_price
from django.shortcuts import redirect, render
from game.api import get_steam_game_details
from .utils import get_basket_wishlist
from django.http import HttpResponse
from django.core import serializers

# Create your views here.
def indexpage(request):        
    context = {}
    top_sellers = Game.objects.order_by('-copies_sold')[:6]
    featured_games_list = FeaturedGame.objects.all()
    featured_games = []
    for feat_game in featured_games_list:
        rating = GameRating.objects.filter(game=feat_game.game)[0]
        total_rating = rating.five_stars + rating.four_stars + rating.three_stars + rating.two_stars + rating.one_stars
        average_rating = float(f"{((rating.five_stars * 5 + rating.four_stars * 4 + rating.three_stars * 3 + rating.two_stars * 2 + rating.one_stars * 1)/(total_rating if total_rating != 0 else 1)):.1f}")

        featured_games.append({
            'game': feat_game.game,
            'total_rating': total_rating,
            'average_rating': average_rating,
            'tag': feat_game.tag,
            'tag_color_code': feat_game.tag_color_code,
        })
    context["top_sellers"] = top_sellers
    context["featured_games"] = featured_games
    context = get_basket_wishlist(request, context)
    # print(get_steam_game_details())
    return render(request, 'core/indexpage.html', context)

def gamepage(request, slug):
    try:
        game = Game.objects.get(slug=slug)
    except Game.DoesNotExist:
        return redirect('indexpage')
    screenshots = GameScreenshot.objects.filter(game=game)
    game_rating = GameRating.objects.get(game=game)
    total_rating = game_rating.five_stars + game_rating.four_stars + game_rating.three_stars + game_rating.two_stars + game_rating.one_stars
    average_rating = (game_rating.five_stars * 5 + game_rating.four_stars * 4 + game_rating.three_stars * 3 + game_rating.two_stars * 2 + game_rating.one_stars * 1)/total_rating if total_rating != 0 else 0
    reviews = GameReview.objects.filter(game=game).order_by('-review_date')
    
    game_genres = GameGenre.objects.get(game=game)
    genre = game_genres.get_genres()

    context = {}
    context['game'] = game
    context['screenshots'] = screenshots
    context['rating'] = {
        'game_rating': game_rating,
        'total': total_rating,
        'average': average_rating
    }
    context['genres'] = genre
    context['reviews'] = reviews
    context = get_basket_wishlist(request, context)
    return render(request, 'core/gamepage.html', context)

def searchpage(request):
    games = Game.objects.filter(display_name__icontains=request.GET.get('q'))
    games_json = serializers.serialize('json', games)
    return HttpResponse(games_json, content_type='application/json')

def resultpage(request):
    games = Game.objects.filter(display_name__icontains=request.GET.get('q'))
    return render(request, 'core/resultpage.html')

@login_required(login_url='indexpage')
def basketpage(request):
    user_basket = Basket.objects.get(buyer=request.user)
    context = {}
    context["user_basket"] = user_basket.games.all()
    context = calculate_basket_price(user_basket, context)
    context = get_basket_wishlist(request, context)
    return render(request, 'core/basketpage.html', context)

@login_required(login_url='indexpage')
def profilepage(request):
    context = {}
    context = get_basket_wishlist(request, context)
    user_profile = UserProfile.objects.get(user=request.user)
    total_avatar_count = ProfileAvatar.objects.all().count()
    context["user_profile"] = user_profile
    context["total_avatar_count"] = total_avatar_count

    recent_orders = GameOrder.objects.filter(buyer=request.user).order_by('-order_date')[:5]
    context["recent_orders"] = recent_orders

    user_wishlist = Wishlist.objects.get(buyer=request.user).games.all()[:5]
    context["user_wishlist"] = user_wishlist

    user_reviews = GameReview.objects.filter(reviewer=request.user).order_by('-review_date')[:5]
    context["user_reviews"] = user_reviews
    return render(request, 'account/profilepage.html', context)