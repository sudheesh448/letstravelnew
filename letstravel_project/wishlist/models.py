from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from admin_side.models import ProductVariantColor  # Import the ProductVariantColor model from the admin_side app



class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist for {self.user.username}"
    

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product_variant_color = models.ForeignKey(ProductVariantColor, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.wishlist.user.username}'s Wishlist Item - {self.product_variant_color.product_variant.product.name} - {self.product_variant_color.color_variant.name}"


