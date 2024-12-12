from django.urls import path
from . import views

urlpatterns = [
    path('add_to_basket/<int:product_id>', views.add_to_basket, name='add_to_basket'),
    path('add_to_wishlist/<int:product_id>', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist_to_basket/<int:product_id>', views.wishlist_to_basket, name='wishlist_to_basket'),
    path('create_order', views.create_order, name='create_order'),
    path('initiate_payment/<total_price>/<order_id>', views.initiate_payment, name='initiate_payment'),
    path('verify_payment', views.verify_payment, name='verify_payment'),
    path('check_voucher', views.check_voucher, name='check_voucher'),
    path('remove_from_basket', views.remove_from_basket, name='remove_from_basket'),
    path('remove_from_wishlist', views.remove_from_wishlist, name='remove_from_wishlist'),
]