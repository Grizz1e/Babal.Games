from django.shortcuts import redirect, render
from game.models import Game, FeaturedGame, GameRating, GameScreenshot, Basket, Wishlist
from django.contrib.auth.decorators import login_required

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

    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.get(buyer=request.user).games.count()
        basket = Basket.objects.get(buyer=request.user)
        basket_count = basket.games.count()
        basket_value = 0
        for game in basket.games.all():
            basket_value += (game.price - game.discount_amount)
        context['wishlist_count'] = wishlist_count
        context['basket_count'] = basket_count
        context['basket_value'] = f"{(basket_value):.2f}"
    else:
        context['wishlist_count'] = 0
        context['basket_count'] =0
        context['basket_value'] = 0.00
    return render(request, 'core/indexpage.html', context)

def gamepage(request, slug):
    try:
        game = Game.objects.get(slug=slug)
    except Game.DoesNotExist:
        return redirect('indexpage')
    screenshots = GameScreenshot.objects.filter(game=game)
    context = {}
    context['game'] = game
    context['screenshots'] = screenshots

    return render(request, 'core/gamepage.html', context)

@login_required(login_url='indexpage')
def basketpage(request):
    user_basket = Basket.objects.get(buyer=request.user)
    price = 0
    for game in user_basket.games.all():
        price += (game.price - game.discount_amount)
    context = {}
    context["user_basket"] = user_basket
    context["basket_price"] = price
    return render(request, 'core/basketpage.html', context)
    

def add_to_wishlist(request):
    if request.user.is_authenticated:
        pass