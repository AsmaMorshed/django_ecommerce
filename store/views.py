from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Product, Category, Order, OrderItem
from .forms import CheckoutForm
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse


def _get_cart(request):
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def _compute_cart_totals(cart):
    subtotal = Decimal('0.00')
    for item in cart.values():
        subtotal += Decimal(str(item['unit_price'])) * item['quantity']
    return subtotal


# ── CATALOG / HOME VIEW
def index(request):
    products   = Product.objects.filter(is_available=True)
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    search_query  = request.GET.get('search', '')
    active_category = None

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    if search_query:
        products = products.filter(name__icontains=search_query)

    # stock management — mark out of stock
    for product in products:
        if product.stock <= 0:
            product.is_available = False
            product.save()

    context = {
        'products':        products,
        'categories':      categories,
        'active_category': active_category,
        'search_query':    search_query,
    }
    return render(request, 'store/index.html', context)


# ── PRODUCT DETAIL VIEW
def product_detail(request, slug):

    product = get_object_or_404(Product, slug=slug, is_available=True)
    images  = product.images.all()
    colors  = product.colors.all()
    sizes   = product.sizes.all()

    context = {
        'product': product,
        'images':  images,
        'colors':  colors,
        'sizes':   sizes,
    }
    return render(request, 'store/product_detail.html', context)


# ── CART: ADD ITEM
def cart_add(request):
    if request.method != 'POST':
        return redirect('index')

    product_id = request.POST.get('product_id')
    color_id = request.POST.get('color_id', '') or ''
    size_id = request.POST.get('size_id', '') or ''
    quantity = int(request.POST.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id, is_available=True)

    if quantity > product.stock:
        messages.error(request, f"Only {product.stock} items available for {product.name}.")
        return redirect('product_detail', slug=product.slug)

    color_name = ''
    if color_id:
        color = product.colors.filter(id=color_id).first()
        color_name = color.name if color else ''

    size_name = ''
    if size_id:
        size = product.sizes.filter(id=size_id).first()
        size_name = size.name if size else ''

    unit_price = product.get_price_for_variant(
        size=size_id or None,
        color=color_id or None
    )

    item_key = f"{product_id}_{color_id}_{size_id}"
    cart = _get_cart(request)

    if item_key in cart:
        new_qty = cart[item_key]['quantity'] + quantity
        if new_qty > product.stock:
            messages.error(request, f"Only {product.stock} items available for {product.name}.")
            return redirect('product_detail', slug=product.slug)
        cart[item_key]['quantity'] = new_qty
    else:
        primary_image = product.images.filter(is_primary=True).first() or product.images.first()
        cart[item_key] = {
            'product_id': str(product.id),
            'product_name': product.name,
            'product_slug': product.slug,
            'image_url': primary_image.image.url if primary_image else '',
            'color_id': color_id,
            'color_name': color_name,
            'size_id': size_id,
            'size_name': size_name,
            'quantity': quantity,
            'unit_price': str(unit_price),
        }

    _save_cart(request, cart)
    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart')


# ── CART: DETAIL
def cart_detail(request):
    cart = _get_cart(request)

    for item_key, item in list(cart.items()):
        try:
            product = Product.objects.get(id=item['product_id'], is_available=True)
            if item['quantity'] > product.stock:
                item['quantity'] = product.stock
                if product.stock == 0:
                    del cart[item_key]
                    _save_cart(request, cart)
                    continue
                messages.warning(request, f"Quantity for {product.name} adjusted to available stock.")
        except Product.DoesNotExist:
            del cart[item_key]
            _save_cart(request, cart)
            messages.warning(request, "Some items were removed as they are no longer available.")
            continue

    _save_cart(request, cart)
    subtotal = _compute_cart_totals(cart)

    context = {
        'cart_items': cart.items(),
        'subtotal': subtotal,
    }
    return render(request, 'store/cart.html', context)


# ── CART: UPDATE QUANTITY
def cart_update(request, item_key):
    if request.method != 'POST':
        return redirect('cart')

    cart = _get_cart(request)
    if item_key not in cart:
        messages.error(request, "Item not found in cart.")
        return redirect('cart')

    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        del cart[item_key]
        messages.success(request, "Item removed from cart.")
    else:
        try:
            product = Product.objects.get(id=cart[item_key]['product_id'], is_available=True)
            if quantity > product.stock:
                messages.error(request, f"Only {product.stock} available for {product.name}.")
            else:
                cart[item_key]['quantity'] = quantity
                messages.success(request, "Cart updated.")
        except Product.DoesNotExist:
            del cart[item_key]
            messages.warning(request, "Item removed — product no longer available.")

    _save_cart(request, cart)
    return redirect('cart')


# ── CART: REMOVE ITEM
def cart_remove(request, item_key):
    if request.method != 'POST':
        return redirect('cart')

    cart = _get_cart(request)
    if item_key in cart:
        del cart[item_key]
        _save_cart(request, cart)
        messages.success(request, "Item removed from cart.")

    return redirect('cart')


# ── CHECKOUT
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect('index')

    # Validate stock for all items
    for item_key, item in list(cart.items()):
        try:
            product = Product.objects.get(id=item['product_id'], is_available=True)
            if item['quantity'] > product.stock:
                messages.error(
                    request,
                    f"{product.name} only has {product.stock} in stock. Please adjust your cart."
                )
                return redirect('cart')
        except Product.DoesNotExist:
            del cart[item_key]
            _save_cart(request, cart)
            messages.warning(request, "Some items were removed as they are no longer available.")
            return redirect('cart')

    subtotal = _compute_cart_totals(cart)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                session_key=request.session.session_key or '',
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                total=subtotal,
            )

            for item in cart.values():
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=item['product_name'],
                    product_price=item['unit_price'],
                    quantity=item['quantity'],
                    color_name=item.get('color_name', ''),
                    size_name=item.get('size_name', ''),
                )
                product.stock -= item['quantity']
                product.save()

            request.session['cart'] = {}
            request.session.modified = True
            messages.success(request, "Order placed successfully!")
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'cart_items': cart.items(),
        'subtotal': subtotal,
    }
    return render(request, 'store/checkout.html', context)


# ── ORDER CONFIRMATION
def order_confirmation(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        session_key=request.session.session_key or ''
    )
    context = {'order': order}
    return render(request, 'store/order_confirmation.html', context)
def initiate_payment(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'store/payment.html', {'order': order})

@csrf_exempt
def payment_success(request):
    order_id = request.POST.get('order_id')
    order = Order.objects.get(id=order_id)
    order.is_paid = True
    order.payment_status = 'Paid'
    order.transaction_id = f"TXN{order.id}00{order.id}"
    order.save()
    return render(request, 'store/payment_success.html', {'order': order})

def payment_fail(request):
    return render(request, 'store/payment_fail.html')
def generate_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 60, "INVOICE")

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 90,  f"Invoice #: INV-{str(order.id)[:8].upper()}")
    p.drawString(50, height - 110, f"Date: {order.created_at.strftime('%d %B %Y')}")

    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, height - 150, "Bill To:")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 170, str(order.full_name))
    p.drawString(50, height - 188, str(order.email))

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50,  height - 230, "Item")
    p.drawString(350, height - 230, "Qty")
    p.drawString(430, height - 230, "Price")
    p.drawString(510, height - 230, "Total")
    p.line(50, height - 235, 560, height - 235)

    y = height - 255
    p.setFont("Helvetica", 11)
    for item in order.items.all():
        p.drawString(50,  y, str(item.product.name)[:35])
        p.drawString(350, y, str(item.quantity))
        p.drawString(430, y, f"{item.product.current_price} BDT")
        p.drawString(510, y, f"{item.quantity * item.product.current_price} BDT")
        y -= 20

    p.line(50, y - 5, 560, y - 5)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(400, y - 25, f"TOTAL: {order.total} BDT")

    p.setFont("Helvetica", 10)
    p.drawString(50, 50, "Thank you for your order! — Southeast University E-Commerce")
    p.showPage()
    p.save()
    return response

from django.http import JsonResponse

def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []
    if query:
        products = Product.objects.filter(
            name__icontains=query, 
            is_available=True
        ).values('name', 'slug')[:6]
        suggestions = list(products)
    return JsonResponse({'suggestions': suggestions})

def order_tracking(request):
    order = None
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        order_id = request.POST.get('order_id')
        try:
            order = Order.objects.get(email=email, id=order_id)
        except Order.DoesNotExist:
            error = "No order found with that email and order ID."
    return render(request, 'store/order_tracking.html', {
        'order': order,
        'error': error
    })