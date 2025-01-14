from game.models import Game, GameOrder, GameCode, \
    GameReview, GameScreenshot, NewGameGenre, \
    MinSystemRequirement, RecommendedSystemRequirement, \
    GameBuild
from django.contrib.auth.decorators import login_required
from account.models import UserProfile, ProfileAvatar
from .models import Basket, Wishlist, FeaturedGame
from core.utils import calculate_basket_price, GameRecommendation
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.core import serializers
from django.contrib import messages
from game.utils import GameRecommendationService
from markdown import markdown

# Create your views here.
def indexpage(request):
    context = {}

    recommentation = GameRecommendationService(user=request.user)
    top_sellers = recommentation.get_top_selling_games()[:6]
    if request.user.is_authenticated:
        for_you = recommentation.get_for_you_games()
        context["for_you"] = for_you
    top_rated = recommentation.get_top_rated_games()

    new_games = Game.objects.order_by('-id')[:6]

    featured_games_list = FeaturedGame.objects.all()
    featured_games = []
    for feat_game in featured_games_list:
        game = feat_game.game

        reviews = GameReview.objects.filter(game=game)

        total_rating = reviews.count()
        if total_rating > 0:
            total_score = sum([review.rating for review in reviews])
            average_rating = total_score / total_rating
        else:
            average_rating = 0

        star_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            star_count[review.rating] += 1

        featured_games.append({
            'game': game,
            'total_rating': total_rating,
            'average_rating': average_rating,
            'star_count': star_count,
            'tag': feat_game.tag,
            'tag_color_code': feat_game.tag_color_code,
        })

    context["top_sellers"] = top_sellers
    context["new_games"] = new_games
    context["featured_games"] = featured_games
    context["top_rated"] = top_rated

    return render(request, 'core/indexpage.html', context)

def gamepage(request, slug):
    try:
        game = Game.objects.get(slug=slug)
    except Game.DoesNotExist:
        return redirect('indexpage')
    if request.user.is_authenticated:
        user_has_ordered = GameOrder.objects.filter(
            buyer=request.user,
            games=game,
            is_payment_successful=True
        ).exists()
    else:
        user_has_ordered = False

    if request.method == "POST" and user_has_ordered:
        review_content = request.POST.get('review_content')
        try:
            rating = int(request.POST.get('rating'))
        except Exception as e:
            messages.error(request, "Invalid rating provided")
            return redirect('gamepage', game.slug)
        
        if len(review_content) < 10:
            messages.error(request, "Review can't be less than 10 characters")
            return redirect('gamepage', game.slug)
        if rating <= 0 or rating > 5:
            messages.error(request, "Rating should be between 1-5 stars")
            return redirect('gamepage', game.slug)
        game_review, created = GameReview.objects.get_or_create(reviewer=request.user, game=game, rating=rating)
        game_review.review = review_content
        game_review.rating = rating
        game_review.save()

         
    recommendation = GameRecommendation(request.user)
    you_might_also_like = recommendation.get_frequently_bought_together(game)

    screenshots = GameScreenshot.objects.filter(game=game)
    reviews = GameReview.objects.filter(game=game).order_by('-review_date')
    try:
        if request.user.is_authenticated:
            user_review_exists = GameReview.objects.filter(reviewer=request.user, game=game).exists()
            if user_review_exists:
                user_review = GameReview.objects.filter(reviewer=request.user, game=game).first()
            else:
                user_review = None
        else:
            user_review = None
    except GameReview.DoesNotExist:
        user_review = None

    already_owned = False
    if request.user.is_authenticated:
        already_owned = game.licensed_to.filter(id=request.user.id).exists()
    build_available = GameBuild.objects.filter(game=game).exists()

    total_rating = reviews.count()
    if total_rating > 0:
        total_score = sum([review.rating for review in reviews])
        average_rating = total_score / total_rating
    else:
        average_rating = 0

    star_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        star_count[review.rating] += 1

    min_req, _ = MinSystemRequirement.objects.get_or_create(game=game)
    rec_req, _ = RecommendedSystemRequirement.objects.get_or_create(game=game)
    

    game.long_description = markdown(game.long_description)
    context = {
        'game': game,
        'screenshots': screenshots,
        'build_available': build_available,
        'already_owned': already_owned,
        'rating': {
            'star_list': list(range(5)),
            'total': total_rating,
            'average': average_rating,
            'star_count': star_count
        },
        'reviews': reviews,
        'user_review': user_review,
        'system_requirement': {
            'min': min_req,
            'rec': rec_req
        },
        'user_purchased_game': user_has_ordered,
        'recommendation': {
            'you_might_also_like': you_might_also_like
        }
    }

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
    return render(request, 'core/basketpage.html', context)

@login_required(login_url='indexpage')
def profilepage(request):
    context = {}
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

def genrepage(request, slug:str):
    try:
        genre = get_object_or_404(NewGameGenre, slug=slug)
        # games = GameGenre.objects.filter(**{genre.lower(): True})
        games = Game.objects.filter(genre=genre).all()
    except NewGameGenre.DoesNotExist:
        return redirect('indexpage')
    print(games)
    context = {}
    context['genre'] = genre.display_name
    context['games'] = games
    return render(request, 'core/genrepage.html', context)