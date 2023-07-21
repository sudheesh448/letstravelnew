from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from order.models import Order
from django.db import models
from admin_side.models import Category
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .function import get_product_variant_colors_by_category

class Coupon(models.Model):
    code = models.CharField(max_length=25, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=0)
    expiry_date = models.DateField()
    is_expired = models.BooleanField(default=False)
    available = models.DecimalField(max_digits=5, decimal_places=0)
    is_percentage = models.BooleanField(default=False)
    min_order_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_claimed = models.DecimalField(max_digits=5, decimal_places=0, null=True, blank=True)
    total_amount_claimed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    

    def save(self, *args, **kwargs):
        if self.expiry_date and str(self.expiry_date) <= str(timezone.now().date()):
            self.is_expired = True
            self.is_active = False
        else:
            self.is_expired = False
        super().save(*args, **kwargs)

class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    applied = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    amount_discounted = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'coupon') 

    def save(self, *args, **kwargs):
        if self.used and not self._state.adding:
            if self.coupon:
                # Increment total_claimed by 1
                self.coupon.total_claimed = (self.coupon.total_claimed or 0) + 1
                # Add amount_discounted to total_amount_claimed
                self.coupon.total_amount_claimed = (self.coupon.total_amount_claimed or 0) + self.amount_discounted
                # Save the updated coupon
                self.coupon.save()
        
        super().save(*args, **kwargs)

#--------------------------------------------------------------------------------------------------------------------------------------

class CategoryOffer(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    offer_description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    total_claimed = models.IntegerField(default=0)
    total_amount_claimed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=False)  # New Boolean field to indicate whether the offer is active

    def __str__(self):
        return f"{self.category.name} - Offer: {self.offer_description}"
    
    def update_is_active_status(self):
        today = timezone.now().date()
        if self.expiry == today:
            self.is_active = False
        elif self.expiry > today:
            self.is_active = True
        else:
            self.is_active = False

@receiver(post_save, sender=CategoryOffer)
def update_product_variant_colors(sender, instance, **kwargs):
    if instance.is_active:
        category_id = instance.category_id
        product_variant_colors = get_product_variant_colors_by_category(category_id)
        # Do something with the product_variant_colors here (e.g., update prices or perform any other action)
        for pvc in product_variant_colors:
            # Assuming you have a field in CategoryOffer model named "discount_percentage"
            discount_percentage = instance.discount_percentage
            new_price = pvc.price - (pvc.price * (discount_percentage / 100))
            pvc.offer_price = new_price
            pvc.on_offer = True
            pvc.save()

@receiver(pre_save, sender=CategoryOffer)
def revert_product_variant_colors(sender, instance, **kwargs):
    try:
        # Fetch the original instance from the database before saving the changes
        original_instance = CategoryOffer.objects.get(pk=instance.pk)
        # Check if the is_active field is changing from True to False
        if original_instance.is_active and not instance.is_active:
            category_id = instance.category_id
            product_variant_colors = get_product_variant_colors_by_category(category_id)
            for pvc in product_variant_colors:
                pvc.offer_price = None
                pvc.on_offer = False
                pvc.save()
    except CategoryOffer.DoesNotExist:
        pass

class UserCategoryOffer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category_offer = models.ForeignKey(CategoryOffer, on_delete=models.CASCADE)
    is_claimed = models.BooleanField(default=False)
    claimed_date = models.DateTimeField(null=True, blank=True)
    discounted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.category_offer.category.name} Offer: {self.category_offer.offer_description}"