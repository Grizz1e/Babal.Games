from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import Game, Basket, GameOrder, Wishlist
from .payment import send_payment_request_to_khalti

# Create your views here.

def add_to_basket(request, product_id):
    user = request.user
    if request.method == "POST" and user.is_authenticated:
        game = Game.objects.get(id=product_id)
        basket, created = Basket.objects.get_or_create(buyer=user)
        basket.games.add(game)
        basket.total_price += (game.price - game.discount_amount)
        basket.save()
        return JsonResponse({
            'success': True,
            'message': f"Added {game.display_name} to the cart"
        })
    return JsonResponse({
        'success': False,
        'message': f"User not authenticated or not a POST method"
    })

def add_to_wishlist(request, product_id):
    user = request.user
    if request.method == "POST" and user.is_authenticated:
        game = Game.objects.get(id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(buyer=user)
        wishlist.games.add(game)
        wishlist.save()
        return JsonResponse({
            'success': True,
            'message': f"Added {game.display_name} to the wishlist"
        })
    return JsonResponse({
        'success': False,
        'message': f"User not authenticated or not a POST method"
    })

def create_order(request):
    user = request.user
    if request.method == "POST" and user.is_authenticated:
        user_basket = Basket.objects.get(buyer=user)
        total_price = 0
        order = GameOrder(buyer=user)
        for game in user_basket.games.all():
            print(game)
            order.games.add(game)
            total_price += (game.price - game.discount_amount)
        order.total_price = total_price
        order.save()
    return redirect('initiate_payment', order)

def initiate_payment(request, order):
    res = send_payment_request_to_khalti(
        return_url="/verify_payment",
        amount=order.total_price,
        order_id=order.order_id,
        order_name="Babal.Games Purchase",
    )
    print(res)
