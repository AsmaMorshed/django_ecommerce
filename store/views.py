from django.shortcuts import render, get_object_or_404
from .models import Product, Category


# ── CATALOG / HOME VIEW
def index(request):

    products   = Product.objects.filter(is_available=True)
    categories = Category.objects.all()

    # ── Category filter
    category_slug = request.GET.get('category')
    active_category = None

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products        = products.filter(category=active_category)

    context = {
        'products':         products,
        'categories':       categories,
        'active_category':  active_category,
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