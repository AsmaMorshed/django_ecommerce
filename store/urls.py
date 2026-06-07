from django.urls import path
from . import views

urlpatterns = [
    path('',
         views.index,
         name='index'),

    path('product/<slug:slug>/',
         views.product_detail,
         name='product_detail'),

    path('cart/',
         views.cart_detail,
         name='cart'),

    path('cart/add/',
         views.cart_add,
         name='cart_add'),

    path('cart/update/<str:item_key>/',
         views.cart_update,
         name='cart_update'),

    path('cart/remove/<str:item_key>/',
         views.cart_remove,
         name='cart_remove'),

    path('checkout/',
         views.checkout,
         name='checkout'),

    path('order/<uuid:order_id>/',
         views.order_confirmation,
         name='order_confirmation'),
         path('payment/<int:order_id>/', views.initiate_payment, name='initiate_payment'),
path('payment/success/', views.payment_success, name='payment_success'),
path('payment/fail/', views.payment_fail, name='payment_fail'),
path('invoice/<uuid:order_id>/', views.generate_invoice, name='generate_invoice'),
path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
path('track-order/', views.order_tracking, name='order_tracking'),
]
