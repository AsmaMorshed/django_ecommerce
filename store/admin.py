# store/admin.py
from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductColor,
    ProductSize,
    ProductImage,
    Order,
    OrderItem,
)


# ── CATEGORY ADMIN
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


# ── PRODUCT IMAGE INLINE
class ProductImageInline(admin.TabularInline):
    model  = ProductImage
    extra  = 3       
    fields = ['image', 'alt_text', 'is_primary']


# ── PRODUCT ADMIN
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display        = [
                            'name',
                            'category',
                            'base_price',
                            'premium_price',
                            'current_price',
                            'stock',
                            'is_available'
                          ]
    list_filter         = ['is_available', 'category']
    search_fields       = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal   = ['colors', 'sizes']   # nice UI for ManyToMany
    inlines             = [ProductImageInline]
    list_editable       = ['is_available', 'stock']


# ── COLOR ADMIN
@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code']


# ── SIZE ADMIN
@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ['name']


# ── ORDER ADMIN
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'color_name', 'size_name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'email', 'session_key']
    readonly_fields = ['session_key', 'full_name', 'email', 'phone', 'address', 'city', 'postal_code', 'total']
    inlines = [OrderItemInline]