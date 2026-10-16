from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from PIL import Image, ImageOps
import os


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    main_image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def discount_amount(self):
        if self.old_price and self.old_price > self.price:
            return self.old_price - self.price
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

        # Ограничитель и нормализатор фото (делает 600x600 с сохранением пропорций)
        if self.main_image and os.path.exists(self.main_image.path):
            try:
                img = Image.open(self.main_image.path)
                target_size = (600, 600)
                img.thumbnail(target_size, Image.Resampling.LANCZOS)

                # Создаем чистый белый холст 600x600 и центрируем фото
                new_img = Image.new("RGB", target_size, (255, 255, 255))
                offset = ((target_size[0] - img.size[0]) // 2, (target_size[1] - img.size[1]) // 2)
                new_img.paste(img, offset)
                new_img.save(self.main_image.path, quality=90, optimize=True)
            except Exception:
                pass

    def __str__(self):
        return self.name

# Остальные модели (Profile, Order, Cart и т.д.) остаются без изменений