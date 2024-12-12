from django.urls import path
from . import views

urlpatterns = [
    path('', views.authpage, name='authpage'),
    path('signin_user', views.signin_user, name='signin_user'),
    path('register_user', views.register_user, name='register_user'),
    path('signout_user', views.signout_user, name='signout_user'),
    path('change_avatar', views.change_avatar, name='change_avatar'),
]