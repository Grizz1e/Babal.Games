from .api import send_payment_request_to_khalti, send_verification_request_to_khalti
from .models import Game, GameCode, GameOrder, GameVoucher
from django.contrib.auth.decorators import login_required
from core.utils import calculate_basket_price
from django.shortcuts import redirect, render
from core.models import Basket, Wishlist
from django.http import JsonResponse
from django.utils import timezone
import uuid

# Create your views here.

@login_required(login_url='authpage')
def add_to_basket(request, product_id):
    user = request.user
    if request.method == "POST":
        game = Game.objects.get(id=product_id)
        basket, created = Basket.objects.get_or_create(buyer=user)
        basket.games.add(game)
        basket.save()
        return redirect('basketpage')
    return JsonResponse({
        'success': False,
        'message': f"User not authenticated or not a POST method"
    })

@login_required(login_url='authpage')
def remove_from_basket(request):
    if request.method == "POST":
        slug = request.POST.get('slug')
        try:
            game = Game.objects.get(slug=slug)
        except Game.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Game not found!'
            })
        basket = Basket.objects.get(buyer=request.user)
        basket.games.remove(game)
        basket.save()
        return JsonResponse({
            'success': True,
            'slug': slug,
            'basket': calculate_basket_price(basket, {}),
            'message': 'Game removed from the basket!'
        })

@login_required(login_url='authpage')
def add_to_wishlist(request, product_id):
    if request.method == "POST":
        game = Game.objects.get(id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(buyer=request.user)
        wishlist.games.add(game)
        wishlist.save()
        return redirect('wishlistpage')
    return JsonResponse({
        'success': False,
        'message': f"User not authenticated or not a POST method"
    })

@login_required(login_url='authpage')
def remove_from_wishlist(request):
    if request.method == "POST":
        slug = request.POST.get('slug')
        try:
            game = Game.objects.get(slug=slug)
        except Game.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Game not found!'
            })
        wishlist = Wishlist.objects.get(buyer=request.user)
        wishlist.games.remove(game)
        wishlist.save()
        return JsonResponse({
            'success': True,
            'slug': slug,
            'message': 'Game removed from the wishlist!'
        })


@login_required(login_url='authpage')
def wishlist_to_basket(request, product_id):
    if request.method == "POST":
        try:
            game = Game.objects.get(id=product_id)
        except Game.DoesNotExist:
            return redirect('wishlistpage')
        wishlist = Wishlist.objects.get(buyer=request.user)
        basket = Basket.objects.get(buyer=request.user)
        wishlist.games.remove(game)
        basket.games.add(game)
        wishlist.save()
        basket.save()
        return redirect('basketpage')

@login_required(login_url='authpage')
def create_order(request):
    if request.method == "POST":
        user = request.user
        voucher_code = request.POST.get('voucher-code')
        if voucher_code != "":
            try:
                voucher = GameVoucher.objects.get(voucher_code=voucher_code.upper())
            except GameVoucher.DoesNotExist:
                pass
            if request.user in voucher.used_by.all():
                pass
            else:
                voucher.used_by.add(user)
                voucher.save()
        user_basket = Basket.objects.get(buyer=user)
        # check if the user has any games in the basket
        if user_basket.games.count() == 0:
            return redirect('basketpage')
        total_price = 0
        order = GameOrder.objects.create(buyer=user)
        for game in user_basket.games.all():
            order.games.add(game)
            total_price += (game.price - game.discount_amount)
        order.total_price = total_price
        order.save()
        user_basket.games.clear()
        user_basket.save()
        return redirect('initiate_payment', int(total_price) * 100, str(order.order_id))

@login_required(login_url='authpage')
def initiate_payment(request, total_price, order_id):
    total_price = int(total_price)
    res = send_payment_request_to_khalti(
        amount={
            "base_amount": int(total_price - (total_price * 0.13)),
            "vat_amount": int((total_price * 0.13))
        },
        order_id=order_id,
        order_name="Babal.Games Purchase",
        full_name=request.user.get_full_name(),
        email=request.user.email,
    )
    order = GameOrder.objects.get(order_id=uuid.UUID(order_id))
    order.pidx = res["pidx"]
    order.save()
    return redirect(f"https://test-pay.khalti.com/?pidx={res["pidx"]}")

def verify_payment(request):
    pidx = request.GET.get('pidx')
    if not pidx:
        return JsonResponse({
            'success': False,
            'message': 'pidx is not provided!'
        })
    order = GameOrder.objects.get(pidx=pidx)
    # check if the order exists or not
    if not order:
        return JsonResponse({
            'success': False,
            'message': 'Order not found!'
        })
    if order.buyer != request.user:
        return JsonResponse({
            'success': False,
            'message': 'Unauthorized access!'
        })
    if order.is_payment_successful:
        return JsonResponse({
            'success': False,
            'message': 'Payment already verified!'
        })
    res = send_verification_request_to_khalti(pidx=pidx)
    if res["status"] == "Completed" and res["refunded"] == False:
        order.is_payment_successful = True
        order.save()

        for game in order.games.all():
            game.copies_sold += 1
            game.save()
            game_code = GameCode.objects.filter(game=game, is_sold=False).first()
            game_code.is_sold = True
            game_code.sold_to = order.buyer
            game_code.date_sold = timezone.now()
            game_code.associated_order_id = order.order_id
            game_code.save()
        return redirect('mykeyspage')
    return JsonResponse({
        'success': False,
        'message': 'Payment not verified!'
    })

@login_required(login_url='authpage')
def check_voucher(request):
    if request.method == "POST":
        voucher_code = request.POST.get('voucher_code')
        total_amount = float(request.POST.get('total_amount'))
        try:
            voucher = GameVoucher.objects.get(voucher_code=voucher_code.upper())
        except GameVoucher.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Voucher not found!'
            })
        if request.user in voucher.used_by.all():
            return JsonResponse({
                'success': False,
                'message': 'Voucher already used by you!'
            })
        if total_amount < voucher.minimum_spend:
            return JsonResponse({
                'success': False,
                'message': 'Minimum spend not met!'
            })
        if voucher.voucher_type == "amount":
            discount_amount = voucher.max_discount_amount
        else:
            discount_amount = (total_amount * voucher.percentage_discount) / 100
            if discount_amount > voucher.max_discount_amount:
                discount_amount = voucher.max_discount_amount
        return JsonResponse({
            'success': True,
            'discount_amount': discount_amount,
            'message': 'Voucher is valid!'
        })


@login_required(login_url='authpage')
def remove_from_basket(request):
    if request.method == "POST":
        slug = request.POST.get('slug')
        try:
            game = Game.objects.get(slug=slug)
        except Game.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Game not found!'
            })
        basket = Basket.objects.get(buyer=request.user)
        basket.games.remove(game)
        basket.save()
        return JsonResponse({
            'success': True,
            'slug': slug,
            'basket': calculate_basket_price(basket, {}),
            'message': 'Game removed from the basket!'
        })