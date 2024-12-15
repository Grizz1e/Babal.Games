from django.shortcuts import render, redirect
from django.contrib.admin.models import LogEntry
from game.models import GameCode,Game, GameScreenshot, GameRating, GameReview, GameGenre
from django.core.paginator import Paginator
from .forms import BannerUploadForm, ScreenshotUploadForm

# Create your views here.

def dashboard_overview(request):
    logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')
    total_sold = GameCode.objects.filter(is_sold=True).count()
    total_remaining = GameCode.objects.filter(is_sold=False).count()

    top_sold_games = Game.objects.all().order_by('-copies_sold')[:5]
    game_list = []
    sales_count = []
    for game in top_sold_games:
        game_list.append(f"{game.display_name}")
        sales_count.append(game.copies_sold)

    p = Paginator(logs, 5)
    page = request.GET.get('page')
    log_entries = p.get_page(page)

    context = {}
    context['log_entries'] = log_entries
    context['total_sales'] = {
        'sold': total_sold,
        'remaining': total_remaining,
    }
    context['top_sales'] = {
        'games': game_list,
        'copies_sold': sales_count,
    }
    return render(request, 'dashboard/overview.html', context)

def dashboard_games(request):
    q = request.GET.get('q')
    if not q:
        game_list = Game.objects.all()
    else:
        game_list = Game.objects.filter(display_name__icontains=q)
    p = Paginator(game_list, 6)
    page = request.GET.get('page')
    games = p.get_page(page)
 
    context = {}
    context['games'] = games
    return render(request, 'dashboard/games.html', context)

def dashboard_game_page(request, slug):
    try:
        game = Game.objects.get(slug=slug)
    except Game.DoesNotExist:
        return redirect('dashboard_games')
    
    if request.method == "POST":
        new_display_name = request.POST.get('display_name')
        new_slug = request.POST.get('slug')
        new_description = request.POST.get('description')
        new_long_description = request.POST.get('long_description')
        new_price = request.POST.get('price')
        new_discount_amount = request.POST.get('discount_amount')
        if new_display_name is not None:
            game.display_name = new_display_name
            game.save()
        if new_slug is not None:
            game.slug = new_slug
            game.save()
        if new_description is not None:
            game.description = new_description
            game.save()
        if new_long_description is not None:
            game.long_description = new_long_description
            game.save()
        if new_price is not None:
            game.price = new_price
            game.save()
        if new_discount_amount is not None:
            game.discount_amount = new_discount_amount
            game.save()

        banner = request.FILES.get('banner', None)
        if banner:
            banner_form = BannerUploadForm(request.POST, request.FILES, instance=game)
            if banner_form.is_valid():
                banner_form.save()
        
                banner = request.FILES.get('banner', None)
        screenshot = request.FILES.get('screenshot', None)
        if screenshot:
            new_screenshot = GameScreenshot.objects.create(game=game, image=screenshot)
            new_screenshot.save()

        if request.POST.get('form_type') == 'genre':
            genre, created = GameGenre.objects.get_or_create(game=game)

            genre.action = 'genre_action' in request.POST
            genre.adventure = 'genre_adventure' in request.POST
            genre.anime = 'genre_anime' in request.POST
            genre.fps = 'genre_fps' in request.POST
            genre.horror = 'genre_horror' in request.POST
            genre.indie = 'genre_indie' in request.POST
            genre.open_world = 'genre_open_world' in request.POST
            genre.racing = 'genre_racing' in request.POST
            genre.rpg = 'genre_rpg' in request.POST
            genre.simulation = 'genre_simulation' in request.POST
            genre.sports = 'genre_sports' in request.POST

            genre.save()

        if request.POST.get('form_type') == 'platform':
            print('platform_mac' in request.POST)
            game.is_available_on_windows = 'platform_windows' in request.POST
            game.is_available_on_linux = 'platform_linux' in request.POST
            game.is_available_on_mac = 'platform_mac' in request.POST

            game.save()


    codes = GameCode.objects.filter(game=game).all()
    screenshots = GameScreenshot.objects.filter(game=game).all()
    rating = GameRating.objects.get(game=game)
    reviews = GameReview.objects.filter(game=game).all()
    genre = GameGenre.objects.get(game=game)

    context = {}
    context['game'] = game
    context['codes'] = codes
    context['screenshots'] = screenshots
    context['rating'] = rating
    context['reviews'] = reviews
    context['genre'] = genre



    return render(request, 'dashboard/dashboard_game.html', context)