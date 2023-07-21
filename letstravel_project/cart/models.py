from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from admin_side.models import Product
from admin_side.models import ProductVariantColor
from django.db.models import Sum

from discount.models import UserCoupon

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    total_items = models.IntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price_before_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_variant_color = models.ForeignKey(ProductVariantColor, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_variant_color.pk} in {self.cart}"

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=CartItem)
@receiver(post_delete, sender=CartItem)
def update_cart_totals(sender, instance, **kwargs):
    cart = instance.cart
    cart.total_items = cart.items.aggregate(total_items=models.Sum('quantity'))['total_items'] or 0
    cart.total_price = cart.items.aggregate(total_price=models.Sum('subtotal'))['total_price'] or 0.00
    cart.total_price_before_discount = cart.items.aggregate(total_price=models.Sum('subtotal'))['total_price'] or 0.00
    cart.save()



    user = cart.user
        # Get all the UserCoupon instances for the user
    user_coupons = UserCoupon.objects.filter(user=user)
        # Iterate over the UserCoupon instances and update the applied field
    for user_coupon in user_coupons:
        if not user_coupon.used:
            user_coupon.applied = False
            user_coupon.save()

@receiver(post_save, sender=CartItem)
def update_cart_totals_on_quantity_change(sender, instance, **kwargs):
    # Calculate subtotal and update cart totals on quantity change
    if instance.quantity != instance.pk:
        instance.subtotal = instance.price * instance.quantity
        instance.cart.save()
