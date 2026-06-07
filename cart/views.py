from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

# Member 2's Product model — adjust import path if their app is named differently
from store.models import Product, ProductColor, ProductSize

from .cart import Cart
from .forms import AddToCartForm, CheckoutForm


# -----------------------------------------------------------------------
# CART DETAIL VIEW
# -----------------------------------------------------------------------
def cart_detail(request):
    """Displays the interactive cart review screen (cart.html)."""
    cart = Cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})


# -----------------------------------------------------------------------
# ADD TO CART
# -----------------------------------------------------------------------
@require_POST
def add_to_cart(request, product_id):
    """
    Called from Member 2's product_detail.html form submission.
    Reads selected color/size from POST data and adds the item.
    """
    cart    = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form    = AddToCartForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add_item(
            product=product,
            quantity=cd['quantity'],
            color=cd.get('color', ''),
            size=cd.get('size', ''),
            override_quantity=cd['override'],
        )
        messages.success(request, f'"{product.name}" added to your cart.')
    return redirect('cart:cart_detail')


# -----------------------------------------------------------------------
# REMOVE FROM CART
# -----------------------------------------------------------------------
@require_POST
def remove_from_cart(request, product_id):
    """Removes a product line from the session cart."""
    cart    = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove_item(product)
    messages.info(request, f'"{product.name}" removed from cart.')
    return redirect('cart:cart_detail')


# -----------------------------------------------------------------------
# CHECKOUT VIEW
# -----------------------------------------------------------------------
def checkout(request):
    """
    Displays delivery & address verification fields (checkout.html).
    On POST validates the form — Member 5 will hook payment logic here.
    """
    cart = Cart(request)

    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    form = CheckoutForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        # Store form data in session for Member 5's payment/order step
        request.session['checkout_data'] = form.cleaned_data
        # Member 5 will take over from here — redirect to payment URL
        return redirect('cart:cart_detail')  # Member 5 will update this   # Member 5's URL name

    context = {
        'cart': cart,
        'form': form,
    }
    return render(request, 'cart/checkout.html', context)
