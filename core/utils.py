from .models import Basket, Wishlist

def get_basket_wishlist(request, context):
    if request.user.is_authenticated:
        wishlisted_games = Wishlist.objects.get(buyer=request.user).games.all()
        wishlist_count = wishlisted_games.count()

        basket = Basket.objects.get(buyer=request.user)
        basket_count = basket.games.count()
        basket_value = 0

        context['wishlisted_games'] = [game.id for game in wishlisted_games]

        for game in basket.games.all():
            basket_value += (game.price - game.discount_amount)
        context['wishlist_count'] = wishlist_count
        context['basket_count'] = basket_count
        context['basket_value'] = f"{(basket_value):.2f}"
    else:
        context['wishlist_count'] = 0
        context['basket_count'] =0
        context['basket_value'] = 0.00
    return context

def calculate_basket_price(basket, context):
    full_price = 0
    final_price = 0
    for game in basket.games.all():
        full_price += game.price
        final_price += (game.price - game.discount_amount)
    discount = full_price - final_price
    context["full_price"] = full_price
    context["discount"] = discount
    context["final_price"] = final_price
    return context