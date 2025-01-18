from django.urls import path
from . import views
from account import views as account_views

urlpatterns = [
    path('', views.indexpage, name='indexpage'),
    path('game/<str:slug>', views.gamepage, name='gamepage'),
    path('basket', views.basketpage, name='basketpage'),
    path('genre/<slug:slug>', views.genrepage, name='genrepage'),
    path('profile/order_history', account_views.orderhistorypage, name='orderhistorypage'),
    path('profile/wishlist', account_views.wishlistpage, name='wishlistpage'),
    path('profile/my-games', account_views.mygamespage, name='mygamespage'),
    path('profile/my_reviews', account_views.myreviewspage, name='myreviewspage'),
    path('profile/settings', account_views.settingspage, name='settingspage'),
    path('profile', views.profilepage, name='profilepage'),

    path('result/', views.resultpage, name='resultpage'),

]