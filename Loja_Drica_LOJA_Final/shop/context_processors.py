from .models import ShopSettings, Favorite

def store_ui(request):
    cart = request.session.get('cart', {})
    count = 0
    if isinstance(cart, dict):
        for quantity in cart.values():
            try: count += min(max(int(quantity), 0), 99)
            except (TypeError, ValueError): pass
    store = ShopSettings.objects.first() or ShopSettings()
    return {
        'cart_count': count,
        'store_info': store,
        'favorite_count': Favorite.objects.filter(user=request.user).count() if request.user.is_authenticated else 0,
    }
