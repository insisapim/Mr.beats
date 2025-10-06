from django.db import models
from django.conf import settings

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    bpm = models.PositiveIntegerField(blank=True, null=True)
    music_key = models.CharField(max_length=8, blank=True, null=True)
    file = models.FileField(upload_to='products/%Y/%m/%d/')
    preview_file = models.FileField(upload_to='products/previews/%Y/%m/%d/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    license_text = models.TextField(blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    theme = models.TextField()
    product_image = models.ImageField(upload_to='products/images/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    downloads = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['seller']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return f"{self.title} — {self.seller}"
