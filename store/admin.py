# store/admin.py
from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductColor,
    ProductSize,
    ProductImage
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