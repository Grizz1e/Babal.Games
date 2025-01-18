from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now, timedelta


from .models import ProfileAvatar, UserProfile
from game.models import GameCode, GameOrder, GameReview, Game
from core.models import Wishlist
from .forms import RegisterForm
from game.utils import GameRecommendationService

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
    messages.error(request, "Invalid Username/Password")
    return redirect('authpage')

@login_required(login_url="authpage")
def signout_user(request):
    logout(request)
    return redirect('indexpage')

def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            
            user = form.save(commit=False)
            
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('authpage')
        else:
            print(form.errors)
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegisterForm()
    
    return render(request, 'account/authpage.html', {'form': form})

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
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            order = GameOrder.objects.get(order_id=order_id)
        except GameOrder.DoesNotExist:
            return redirect('orderhistorypage')
        order.status = 3
        order.save()
    context = {}
    user_profile = UserProfile.objects.get(user=request.user)
    total_avatar_count = ProfileAvatar.objects.all().count()
    context["user_profile"] = user_profile
    context["total_avatar_count"] = total_avatar_count

    user_orders = GameOrder.objects.filter(buyer=request.user).order_by('-order_date')
    for order in user_orders:
        if order.status == 1:
            expiration_time = order.order_date + timedelta(minutes=30)
            if now() > expiration_time:
                order.status = 4
                order.save()
    context["orders"] = user_orders
    return render(request, 'account/orderhistorypage.html', context)

@login_required(login_url="authpage")
def wishlistpage(request):
    context = {}
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
def mygamespage(request):
    context = {}
    user_profile = UserProfile.objects.get(user=request.user)
    total_avatar_count = ProfileAvatar.objects.all().count()
    context["user_profile"] = user_profile
    context["total_avatar_count"] = total_avatar_count

    licensed_games = Game.objects.filter(licensed_to=request.user)
    context["licensed_games"] = licensed_games
    return render(request, 'account/mygames.html', context)

@login_required(login_url="authpage")
def myreviewspage(request):
    context = {}
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
    user = request.user
    if request.method == "POST":
        new_email = request.POST.get('email')
        new_first_name = request.POST.get('first_name')
        new_last_name = request.POST.get('last_name')
        delete_user = request.POST.get('delete_user')

        current_pass = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')
        if current_pass is not None and new_pass is not None and new_pass == confirm_pass:
            if user.check_password(current_pass):
                user.set_password(new_pass)
                user.save()
                messages.success(request, "Password Changed")



        if new_email is not None:
            user.email = new_email
            user.save()
            messages.success(request, "Email Changed")

        if new_first_name is not None:
            user.first_name = new_first_name
            user.save()
            messages.success(request, "First Name Changed")

        if new_last_name is not None:
            user.last_name = new_last_name
            user.save()
            messages.success(request, "Last Name Changed")

        if delete_user is not None:
            user.delete()
            messages.success(request, "User deleted successfully")
    context = {}
    user_profile = UserProfile.objects.get(user=request.user)
    total_avatar_count = ProfileAvatar.objects.all().count()
    context["user_profile"] = user_profile
    context["total_avatar_count"] = total_avatar_count
    return render(request, 'account/settingspage.html', context)