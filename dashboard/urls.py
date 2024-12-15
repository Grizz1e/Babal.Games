from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test
from . import views

def is_admin(user):
    return user.is_authenticated and user.is_staff

urlpatterns = [
    path('', user_passes_test(is_admin)(views.dashboard_overview), name="dashboard_overview"),
    path('games/', user_passes_test(is_admin)(views.dashboard_games), name="dashboard_games"),
    path('games/<str:slug>', user_passes_test(is_admin)(views.dashboard_game_page), name="dashboard_game_page")
]
