from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import datetime
from order.models import Order
from django.db import models
from admin_side.models import Category
from django.db import models
from django.contrib.auth.models import User

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



from django.db import models

class CategoryOffer(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    offer_description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    total_claimed = models.IntegerField(default=0)
    total_amount_claimed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expiry = models.DateTimeField(default=datetime.date.today)
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


class UserCategoryOffer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category_offer = models.ForeignKey(CategoryOffer, on_delete=models.CASCADE)
    is_claimed = models.BooleanField(default=False)
    claimed_date = models.DateTimeField(null=True, blank=True)
    discounted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.category_offer.category.name} Offer: {self.category_offer.offer_description}"
