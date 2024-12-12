from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse


from .models import ProfileAvatar, UserProfile
from game.models import GameCode, GameOrder, GameReview
from core.utils import get_basket_wishlist
from core.models import Wishlist
from .forms import RegisterForm

# Create your views here.
def authpage(request):
    return render(request, 'account/authpage.html')

def signin_user(request):
    if request.method == "POST":
        username_email = request.POST['username-email']
        password = request.POST['password']
        try:
            account = authenticate(username=User.objects.get(email=username_email).username, password=password)
            if account is not None:
                login(request, account)
                return redirect('indexpage')
        except:
            account = authenticate(username=username_email, password=password)
            if account is not None:
                login(request, account)
                return redirect('indexpage')
    return redirect('authpage')

@login_required(login_url="authpage")
def signout_user(request):
    logout(request)
    return redirect('indexpage')

def register_user(request):
    if request.method == "POST":

        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('indexpage')
    return redirect('registerpage')

@login_required(login_url="authpage")
def change_avatar(request):
    if request.method == "POST":
        avatar_id = request.POST.get("avatar_id")
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.avatar_id = int(avatar_id)
        user_profile.save()
        return JsonResponse({
            'success': True,
            'message': "Avatar changed successfully"
        })
    

@login_required(login_url="authpage")
def orderhistorypage(request):
    context = {}
    context = get_basket_wishlist(request, context)
    user_profile = UserProfile.objects.get(user=request.user)
    total_avatar_count = ProfileAvatar.objects.all().count()
    context["user_profile"] = user_profile
    context["total_avatar_count"] = total_avatar_count

    user_orders = GameOrder.objects.filter(buyer=request.user).order_by('-order_date')
    context["user_orders"] = user_orders
    return render(request, 'account/orderhistorypage.html', context)

@login_required(login_url="authpage")
def wishlistpage(request):
    context = {}
    context = get_basket_wishlist(request, context)
    user_profile = UserProfile.objects.get(user=request.user)
    total_avatar_count = ProfileAvatar.objects.all().count()
    context["user_profile"] = user_profile
    context["total_avatar_count"] = total_avatar_count

    sort = request.GET.get("sort")
    if sort is None:
        sort = "display_name"
    wishlisted_games = Wishlist.objects.get(buyer=request.user).games.all().order_by(f"{sort}")
    context["wishlisted_games"] = wishlisted_games
    return render(request, 'account/wishlistpage.html', context)

@login_required(login_url="authpage")
def mykeyspage(request):
    context = {}
    context = get_basket_wishlist(request, context)
    user_profile = UserProfile.objects.get(user=request.user)
    total_avatar_count = ProfileAvatar.objects.all().count()
    context["user_profile"] = user_profile
    context["total_avatar_count"] = total_avatar_count

    game_keys = GameCode.objects.filter(sold_to=request.user)
    context["game_keys"] = game_keys
    return render(request, 'account/mykeyspage.html', context)

@login_required(login_url="authpage")
def myreviewspage(request):
    context = {}
    context = get_basket_wishlist(request, context)
    user_profile = UserProfile.objects.get(user=request.user)
    total_avatar_count = ProfileAvatar.objects.all().count()

    user_reviews = GameReview.objects.filter(reviewer=request.user).order_by('-review_date')
    game_keys = GameCode.objects.filter(sold_to=request.user)
    context["game_keys"] = game_keys
    context["user_reviews"] = user_reviews
    context["user_profile"] = user_profile
    context["total_avatar_count"] = total_avatar_count
    # user_rating = []
    # for review in user_reviews:
    #     user_rating.append({
    #         "game": review.game
    #     })

    return render(request, 'account/myreviewspage.html', context)

@login_required(login_url="authpage")
def settingspage(request):
    context = {}
    context = get_basket_wishlist(request, context)
    user_profile = UserProfile.objects.get(user=request.user)
    total_avatar_count = ProfileAvatar.objects.all().count()
    context["user_profile"] = user_profile
    context["total_avatar_count"] = total_avatar_count
    return render(request, 'account/settingspage.html', context)