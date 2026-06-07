from .cart import Cart


def cart_context(request):
    """
    Custom Context Processor — makes `cart` and `cart_count` available
    in EVERY template automatically (including Member 1's base.html navbar).

    Register in settings.py → TEMPLATES → OPTIONS → context_processors:
        'cart.context_processors.cart_context',
    """
    cart = Cart(request)
    return {
        'cart':       cart,
        'cart_count': cart.get_item_count(),
    }
