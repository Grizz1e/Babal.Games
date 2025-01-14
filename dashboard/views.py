from django.shortcuts import render, redirect
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from game.models import GameCode,Game, GameScreenshot, GameRating, \
    GameReview, NewGameGenre, MinSystemRequirement, \
    RecommendedSystemRequirement, GameOrder, GameBuild, \
    GameVoucher
from account.models import UserProfile
from django.core.paginator import Paginator
from django.utils.timezone import now
from .forms import BannerUploadForm, ScreenshotUploadForm, BuildUploadForm
from game.utils import get_weekly_revenue
from markdown import markdown

# Create your views here.

def dashboard_overview(request):
    logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')
    total_sold = GameCode.objects.filter(is_sold=True).count()
    total_remaining = GameCode.objects.filter(is_sold=False).count()

    p = Paginator(logs, 5)
    page = request.GET.get('page')
    log_entries = p.get_page(page)

    labels, revenue = get_weekly_revenue()

    context = {}
    context['log_entries'] = log_entries
    context['total_sales'] = {
        'sold': total_sold,
        'remaining': total_remaining,
    }
    context['last_week'] = {
        'labels': labels,
        'revenue': revenue
    }
    context['total_games'] = Game.objects.count()
    context['total_users'] = User.objects.count()
    context['total_price'] = GameOrder.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
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

def dashboard_game_page(request, id):
    try:
        game = Game.objects.get(id=id)
    except Game.DoesNotExist:
        return redirect('dashboard_games')
    
    if request.method == "POST":
        new_display_name = request.POST.get('display_name')
        new_slug = request.POST.get('slug')
        new_description = request.POST.get('description')
        new_long_description = request.POST.get('long_description')
        new_price = request.POST.get('price')
        new_discount_amount = request.POST.get('discount_amount')
        new_additional_note = request.POST.get('additional_note')
        new_developer = request.POST.get('game_developer')
        new_publisher = request.POST.get('game_publisher')
        new_support_url = request.POST.get('game_support')
        new_steam_id = request.POST.get('steam_id')
        new_yt_trailer_id = request.POST.get('yt_trailer_id')

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
        if new_steam_id is not None:
            game.steam_id = new_steam_id
            game.save()
        if new_yt_trailer_id is not None:
            game.yt_trailer_id = new_yt_trailer_id
            game.save()
        
        if new_additional_note is not None:
            m, z = MinSystemRequirement.objects.get_or_create(game=game)
            r, z = RecommendedSystemRequirement.objects.get_or_create(game=game)

            m.additional_note = r.additional_note = new_additional_note

            m.save()
            r.save()
        
        if new_developer is not None:
            game.developer = new_developer
            game.save()
        if new_publisher is not None:
            game.publisher = new_publisher
            game.save()
        if new_support_url is not None:
            game.support_url = new_support_url
            game.save()

        banner = request.FILES.get('banner', None)
        if banner:
            banner_form = BannerUploadForm(request.POST, request.FILES, instance=game)
            if banner_form.is_valid():
                banner_form.save()

        screenshot = request.FILES.get('screenshot', None)
        if screenshot:
            new_screenshot = GameScreenshot.objects.create(game=game, image=screenshot)
            new_screenshot.save()

        if request.POST.get('form_type') == 'genre':
            selected_genre_slugs = [key.replace("genre_", "") for key in request.POST.keys() if key.startswith("genre_")]
            
            selected_genres = NewGameGenre.objects.filter(slug__in=selected_genre_slugs)

            game.genre.set(selected_genres)

            game.save()

        if request.POST.get('form_type') == 'platform':
            game.is_available_on_windows = 'platform_windows' in request.POST
            game.is_available_on_linux = 'platform_linux' in request.POST
            game.is_available_on_mac = 'platform_mac' in request.POST

            game.save()

        if request.POST.get('form_type') == 'min-requirement':
            min_requirement, created = MinSystemRequirement.objects.get_or_create(game=game)
            min_requirement.os = request.POST.get('min_os')
            min_requirement.processor = request.POST.get('min_processor')
            min_requirement.memory = request.POST.get('min_memory')
            min_requirement.graphics = request.POST.get('min_graphics')
            min_requirement.storage = request.POST.get('min_storage')

            min_requirement.save()

        if request.POST.get('form_type') == 'rec-requirement':
            rec_requirement, created = RecommendedSystemRequirement.objects.get_or_create(game=game)
            rec_requirement.os = request.POST.get('rec_os')
            rec_requirement.processor = request.POST.get('rec_processor')
            rec_requirement.memory = request.POST.get('rec_memory')
            rec_requirement.graphics = request.POST.get('rec_graphics')
            rec_requirement.storage = request.POST.get('rec_storage')

            rec_requirement.save()

        


    codes = GameCode.objects.filter(game=game).all()
    screenshots = GameScreenshot.objects.filter(game=game).all()
    rating = GameRating.objects.get(game=game)
    reviews = GameReview.objects.filter(game=game).all()
    genres = NewGameGenre.objects.all()
    associated_genres = game.genre.all()

    min_system_requirement, created = MinSystemRequirement.objects.get_or_create(game=game)
    rec_system_requirement, created = RecommendedSystemRequirement.objects.get_or_create(game=game)

    context = {}
    context['game'] = game
    context['codes'] = codes
    context['screenshots'] = screenshots
    context['rating'] = rating
    context['reviews'] = reviews
    context['genres'] = {
        'all': genres,
        'associated': associated_genres
    }
    context['system_requirements'] = {
        'min': min_system_requirement,
        'recommended': rec_system_requirement
    }



    return render(request, 'dashboard/dashboard_game.html', context)

def dashboard_add_game(request):
    if request.method == "POST":
        display_name = request.POST.get('display_name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        long_description = request.POST.get('long_description')
        price = request.POST.get('price')
        discount_amount = request.POST.get('discount_amount')
        additional_note = request.POST.get('additional_note')
        developer = request.POST.get('game_developer')
        publisher = request.POST.get('game_publisher')
        support_url = request.POST.get('game_support')
        steam_id = request.POST.get('steam_id')
        yt_trailer_id = request.POST.get('yt_trailer_id')


        game, created = Game.objects.get_or_create(display_name=display_name, slug=slug, \
                            description=description, long_description=long_description, price=price, \
                            steam_id=steam_id, yt_trailer_id=yt_trailer_id, \
                            discount_amount=discount_amount, developer=developer, \
                            publisher=publisher, support_url=support_url)
        game.is_available_on_windows = 'platform_windows' in request.POST
        game.is_available_on_linux = 'platform_linux' in request.POST
        game.is_available_on_mac = 'platform_mac' in request.POST


        selected_genre_slugs = [key.replace("genre_", "") for key in request.POST.keys() if key.startswith("genre_")]
        selected_genres = NewGameGenre.objects.filter(slug__in=selected_genre_slugs)
        game.genre.set(selected_genres)

        banner = request.FILES.get('banner', None)
        if banner:
            banner_form = BannerUploadForm(request.POST, request.FILES, instance=game)
            if banner_form.is_valid():
                banner_form.save()

                banner = request.FILES.get('banner', None)

        game.save()

        build_file = request.FILES.get('game-file', None)
        if build_file:
            new_build = GameBuild.objects.create(game=game, zip_file=build_file)
            new_build.save()

        min_requirement, created = MinSystemRequirement.objects.get_or_create(game=game)
        min_requirement.os = request.POST.get('min_os')
        min_requirement.processor = request.POST.get('min_processor')
        min_requirement.memory = request.POST.get('min_memory')
        min_requirement.graphics = request.POST.get('min_graphics')
        min_requirement.storage = request.POST.get('min_storage')
        min_requirement.save()

        rec_requirement, created = RecommendedSystemRequirement.objects.get_or_create(game=game)
        rec_requirement.os = request.POST.get('rec_os')
        rec_requirement.processor = request.POST.get('rec_processor')
        rec_requirement.memory = request.POST.get('rec_memory')
        rec_requirement.graphics = request.POST.get('rec_graphics')
        rec_requirement.storage = request.POST.get('rec_storage')
        rec_requirement.save()

        if additional_note is not None:
            min_requirement.additional_note = rec_requirement.additional_note = additional_note
            min_requirement.save()
            rec_requirement.save()


    genres = NewGameGenre.objects.all()
    context = {}
    context['genres'] = {
        'all': genres
    }
    return render(request, 'dashboard/add_game.html', context)

def dashboard_builds(request):
    q = request.GET.get('q')
    if not q:
        builds = GameBuild.objects.all().order_by("-date_added")
    else:
        builds = GameBuild.objects.filter(game__display_name__icontains=q).order_by("-date_added")

    p = Paginator(builds, 10)
    page = request.GET.get('page')
    builds = p.get_page(page)
    context = {
        'builds': builds
    }
    return render(request, 'dashboard/builds.html', context)

def dashboard_add_build(request):
    q = request.GET.get('q')
    
    if not q:
        game_list = Game.objects.all().order_by('display_name')
    else:
        game_list = Game.objects.filter(display_name__icontains=q).order_by('display_name')
    
    games_with_build_counts = game_list.annotate(
        total_builds=Count('gamebuild')
    )
    
    page_number = request.GET.get('page')
    paginator = Paginator(games_with_build_counts, 5)
    page = paginator.get_page(page_number)

    context = {
        'games': page,
        'search_query': q,
    }

    return render(request, 'dashboard/add_build.html', context)

def dashboard_add_build_game(request, slug):
    try:
        game = Game.objects.get(slug=slug)
    except Game.DoesNotExist:
        return redirect('dashboard_add_build')
    if request.method == "POST":
        file = request.FILES.get('build-field', None)
        if file:
            new_build = GameBuild.objects.create(game=game, zip_file=file)
            new_build.save()
        return redirect('dashboard_builds')
    return render(request, 'dashboard/add_build_game.html')

def dashboard_genres(request):
    q = request.GET.get('q')
    if not q:
        genres = NewGameGenre.objects.all().order_by("display_name")
    else:
        genres = NewGameGenre.objects.filter(display_name__icontains=q).order_by("display_name")

    p = Paginator(genres, 21)
    page = request.GET.get('page')
    genres = p.get_page(page)
    context = {
        'genres': genres
    }
    return render(request, 'dashboard/genres.html', context)

def dashboard_add_genre(request):
    context = {}
    if request.method == "POST":
        display_name = request.POST.get('display_name')
        slug = request.POST.get('slug')

        genre = NewGameGenre.objects.create(display_name=display_name, slug=slug)
        genre.save()
        return redirect('dashboard_genres')
    return render(request, 'dashboard/add_genre.html', context)

def dashboard_vouchers(request):
    context = {}
    q = request.GET.get('q')
    if not q:
        vouchers = GameVoucher.objects.all().order_by("voucher_code")
    else:
        vouchers = GameVoucher.objects.filter(voucher_code__icontains=q).order_by("voucher_code")
    p = Paginator(vouchers, 6)
    page = request.GET.get('page')
    vouchers = p.get_page(page)
    context = {
        'vouchers': vouchers
    }
    return render(request, 'dashboard/vouchers.html', context)

def dashboard_add_voucher(request):
    if request.method == "POST":
        voucher_code = request.POST.get('voucher_code')
        voucher_type = request.POST.get('voucher_type')
        minimum_spend = request.POST.get('minimum_spend')
        max_discount_amount = request.POST.get('max_discount_amount')
        percentage_discount = request.POST.get('percentage_discount')

        voucher = GameVoucher.objects.create(voucher_code=voucher_code, voucher_type=voucher_type,
                                             minimum_spend=minimum_spend, max_discount_amount=max_discount_amount,
                                             percentage_discount=percentage_discount)

        voucher.save()
        return redirect('dashboard_vouchers')
    context = {}
    return render(request, 'dashboard/add_voucher.html', context)

def dashboard_users(request):
    context = {}
    q = request.GET.get('q')
    result_type = request.GET.get('type')

    if not result_type:
        result_type = ""
        if not q:
            users = User.objects.all().order_by("username")
        else:
            users = User.objects.filter(username__icontains=q).order_by("username")
    else:
        if not q:
            users = User.objects.filter(is_staff=True).order_by("username")
        else:
            users = User.objects.filter(username__icontains=q, is_staff=True).order_by("username")
    p = Paginator(users, 6)
    page = request.GET.get('page')
    users = p.get_page(page)
    context = {
        'users': users,
        'current_time': now(),
        'result_type': result_type
    }

    return render(request, 'dashboard/users.html', context)

def dashboard_manage_user(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return redirect('dashboard_users')
    if request.method == "POST":
        new_username = request.POST.get('username')
        new_email = request.POST.get('email_address')
        new_first_name = request.POST.get('first_name')
        new_last_name = request.POST.get('last_name')

        delete_user = request.POST.get('delete_user')

        admin_status = 'is_admin' in request.POST
        staff_status = 'is_staff' in request.POST
        active_status = 'is_active' in request.POST

        if new_username is not None:
            user.username = new_username
            user.save()
        if new_email is not None:
            user.email = new_email
            user.save()
        if new_first_name is not None:
            user.first_name = new_first_name
            user.save()
        if new_last_name is not None:
            user.last_name = new_last_name
            user.save()
        if admin_status is not None:
            user.is_superuser = admin_status
            user.save()
        if staff_status is not None:
            user.is_staff = staff_status
            user.save()
        if active_status is not None:
            user.is_active = active_status
            user.save()

        if delete_user is not None:
            user.delete()
            return redirect('dashboard_users')
    user_profile = UserProfile.objects.get(user=user)
    context = {
        'user': user,
        'user_profile': user_profile
    }
    
    return render(request, 'dashboard/manage_user.html', context)