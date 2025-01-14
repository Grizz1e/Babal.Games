from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test
from . import views

def is_admin(user):
    return user.is_authenticated and user.is_staff

urlpatterns = [
    path('', user_passes_test(is_admin)(views.dashboard_overview), name="dashboard_overview"),
    path('games/', user_passes_test(is_admin)(views.dashboard_games), name="dashboard_games"),
    path('genres/', user_passes_test(is_admin)(views.dashboard_genres), name="dashboard_genres"),
    path('genres/add/', user_passes_test(is_admin)(views.dashboard_add_genre), name="dashboard_add_genre"),
    path('games/add/', user_passes_test(is_admin)(views.dashboard_add_game), name="dashboard_add_game"),
    path('games/<int:id>/', user_passes_test(is_admin)(views.dashboard_game_page), name="dashboard_game_page"),
    path('builds/', user_passes_test(is_admin)(views.dashboard_builds), name="dashboard_builds"),
    path('builds/add/', user_passes_test(is_admin)(views.dashboard_add_build), name="dashboard_add_build"),
    path('vouchers/', user_passes_test(is_admin)(views.dashboard_vouchers), name="dashboard_vouchers"),
    path('vouchers/add/', user_passes_test(is_admin)(views.dashboard_add_voucher), name="dashboard_add_voucher"),
    path('builds/add/<slug:slug>/', user_passes_test(is_admin)(views.dashboard_add_build_game), name="dashboard_add_build_game"),
    path('users/', user_passes_test(is_admin)(views.dashboard_users), name="dashboard_users"),
    path('users/manage/<int:id>', user_passes_test(is_admin)(views.dashboard_manage_user), name="dashboard_manage_user"),
]
