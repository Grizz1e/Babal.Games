from django.urls import path
from . import views

urlpatterns = [
    path('add_to_basket/<int:product_id>', views.add_to_basket, name='add_to_basket'),
    path('create_order', views.create_order, name='create_order'),
    path('initiate_payment', views.initiate_payment, name='initiate_payment'),
]