# store/models.py
# ── ADD BELOW Member 1's BaseModel and Category ──────────────────────────────
import uuid
from django.db import models


# ── ABSTRACT BASE MODEL ───────────
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ── CATEGORY ─────────
class Category(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

# ── COLOR VARIANT TABLE


class ProductColor(BaseModel):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(
        max_length=7,
        blank=True,
        help_text="Enter hex color code e.g. #FF0000"
    )

    def __str__(self):
        return self.name


# ── SIZE VARIANT TABLE
class ProductSize(BaseModel):
    name = models.CharField(
        max_length=20,
        help_text="e.g. S, M, L, XL or 38, 39, 40"
    )

    def __str__(self):
        return self.name


# ── MAIN PRODUCT TABLE
class Product(BaseModel):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Standard product price"
    )
    premium_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Price when variant (color/size) is selected"
    )
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    colors = models.ManyToManyField(ProductColor, blank=True)
    sizes = models.ManyToManyField(ProductSize,  blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    # ── Dynamic Pricing Property
    @property
    def current_price(self):

        if self.premium_price:
            return self.premium_price
        return self.base_price

    def get_price_for_variant(self, size=None, color=None):

        if (size or color) and self.premium_price:
            return self.premium_price
        return self.base_price


# ── PRODUCT IMAGE TABLE
class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"
