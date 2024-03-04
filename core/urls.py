from django.urls import path
from . import views

urlpatterns = [
    path('', views.indexpage, name='indexpage'),
    path('game/<str:slug>', views.gamepage, name='gamepage'),
    path('basket', views.basketpage, name='basketpage')
]