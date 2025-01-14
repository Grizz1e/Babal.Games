from .api import send_payment_request_to_khalti, send_verification_request_to_khalti
from .models import Game, GameCode, GameOrder, \
    GameVoucher, NewGameGenre, GameBuild
from django.contrib.auth.decorators import login_required
from core.utils import calculate_basket_price
from django.shortcuts import redirect, render
from core.models import Basket, Wishlist
from django.http import JsonResponse, FileResponse, Http404
from django.utils import timezone
from django.contrib import messages
import uuid, os
from .utils import voucher_applicable

# Create your views here.

@login_required(login_url='authpage')
def add_to_basket(request, product_id):
    user = request.user
    if request.method == "POST":
        game = Game.objects.get(id=product_id)
        if not GameBuild.objects.filter(game=game).exists():
            messages.error(request, "Product Out of Stock")
            return redirect('gamepage', game.slug)
        elif game.licensed_to.filter(id=request.user.id).exists():
            messages.error(request, "You already own this product")
            return redirect('gamepage', game.slug)
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
        if not GameBuild.objects.filter(game=game).exists():
            messages.error(request, "Product Out of Stock")
            return redirect('gamepage', game.slug)
        elif game.licensed_to.filter(id=request.user.id).exists():
            messages.error(request, "You already own this product")
            return redirect('gamepage', game.slug)
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
        print(voucher_code)
        voucher_applied = False
        if voucher_code != "":
            try:
                voucher = GameVoucher.objects.get(voucher_code=voucher_code.upper())
                voucher_applied = True
            except GameVoucher.DoesNotExist:
                return redirect('basketpage')
            if request.user in voucher.used_by.all():
                return redirect('basketpage')
        user_basket = Basket.objects.get(buyer=user)
        # check if the user has any games in the basket
        if user_basket.games.count() == 0:
            return redirect('basketpage')
        total_price = 0
        order = GameOrder.objects.create(buyer=user, status=1)
        for game in user_basket.games.all():
            order.games.add(game)
            total_price += (game.price - game.discount_amount)
        order.total_price = total_price
        if voucher_applied:
            if voucher_applicable(voucher, order, request):
                voucher.used_by.add(user)
                voucher.save()
                order.voucher = voucher
                discount_amount = 0
                if voucher.voucher_type == "amount":
                    discount_amount = voucher.max_discount_amount
                else:
                    discount_amount = (total_price * voucher.percentage_discount) / 100
                    if discount_amount > voucher.max_discount_amount:
                        discount_amount = voucher.max_discount_amount
                total_price -= discount_amount
                order.voucher_amount = discount_amount
        order.save()
        user_basket.games.clear()
        user_basket.save()
        print(total_price)
        return redirect('initiate_payment', float(total_price) * 100, str(order.order_id))

@login_required(login_url='authpage')
def initiate_payment(request, total_price, order_id):
    total_price = float(total_price)
    res = send_payment_request_to_khalti(
        amount={
            "base_amount": float(total_price - (total_price * 0.13)),
            "vat_amount": float(total_price * 0.13)
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
        order.status = 2
        order.save()

        for game in order.games.all():
            game.licensed_to = order.buyer
            game.save()
        return redirect('mygamespage')
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
    
def get_base_info(request):
    genres = NewGameGenre.objects.all().order_by('-display_name').values()
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.get(buyer=request.user).games.count()
        basket = Basket.objects.get(buyer=request.user)
        basket_count = basket.games.count()
        basket_value = 0
        for game in basket.games.all():
            basket_value += (game.price - game.discount_amount)
    else:
        wishlist_count = 0
        basket_count = 0
        basket_value = 0.00
    context = {}
    context['genres'] = list(genres)
    context['wishlist'] = {
        'count': wishlist_count
    }
    context['basket'] = {
        'count': basket_count,
        'value': basket_value
    }
    return JsonResponse(context, safe=False)

@login_required(login_url='authpage')
def remove_build(request):
    if request.method == "POST" and request.user.is_staff:
        try:
            id = request.POST.get('id')
            GameBuild.objects.get(id=id).delete()
        except GameBuild.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred!'
            })
        return JsonResponse({
            'success': True,
            'message': 'Build removed!'
        })
    return JsonResponse({
        'success': False,
        'message': 'An error occurred!'
    })

@login_required(login_url='authpage')
def remove_genre(request):
    if request.method == "POST" and request.user.is_staff:
        try:
            slug = request.POST.get('slug')
            NewGameGenre.objects.get(slug=slug).delete()
        except NewGameGenre.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred!'
            })
        return JsonResponse({
            'success': True,
            'message': 'Genre removed!'
        })
    return JsonResponse({
        'success': False,
        'message': 'An error occurred!'
    })

@login_required(login_url='authpage')
def remove_voucher(request):
    if request.method == "POST" and request.user.is_staff:
        try:
            id = request.POST.get('id')
            GameVoucher.objects.get(id=id).delete()
        except GameVoucher.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Voucher does not exist!'
            })
        return JsonResponse({
            'success': True,
            'message': 'Voucher removed!'
        })
    return JsonResponse({
        'success': False,
        'message': 'An error occurred!'
    })

@login_required(login_url='authpage')
def download_game(request, slug):
    if request.user.is_authenticated and request.method == "POST":
        try:
            try:
                game = Game.objects.get(slug=slug)
            except Game.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': "File does not exist"
                })
            game_build = GameBuild.objects.filter(game=game).order_by('-date_added').first()
        except GameBuild.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': "File does not exist"
            })
        if game.licensed_to.filter(id=request.user.id).exists():
            file_path = game_build.zip_file.path
            if not os.path.exists(file_path):
                raise Http404("File not found")
        
            response = FileResponse(
                open(file_path, 'rb'),
                as_attachment=True,
                filename=f"{game_build.game.slug}_build_{game_build.id}"
            )
            
            response['Content-Type'] = 'application/zip'
            
            return response
    else:
        return JsonResponse({
            'success': False,
            'message': "No permission to access the file"
        })