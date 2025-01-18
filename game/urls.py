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

    path('get_base_info', views.get_base_info, name="get_base_info"),
    path('remove_build', views.remove_build, name="remove_build"),
    path('remove_genre', views.remove_genre, name="remove_genre"),
    path('remove_voucher', views.remove_voucher, name="remove_voucher"),
    path('remove_review', views.remove_review, name="remove_review"),

    path('download/<slug:slug>', views.download_game, name="download_game"),

    path('search', views.searchpage, name="search_product"),
]