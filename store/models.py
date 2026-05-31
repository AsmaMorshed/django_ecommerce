# store/models.py
import uuid
from django.db import models


# ── ABSTRACT BASE MODEL ──────────────────────────────────────────────────────
class BaseModel(models.Model):
    """
    Every model in this project inherits from this class.
    UUID replaces insecure auto-increment integer IDs.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True   # ← No database table is created for this


# ── CATEGORY MODEL ───────────────────────────────────────────────────────────
class Category(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name
