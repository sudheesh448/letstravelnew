import calendar
import datetime

from django.db import models

# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError
from admin_side.models import ProductVariantColor
from userprofile.models import UserAddress
from products.models import *
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.db.models import Sum

# # Create your models here.


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING','pending'),
        ('PAID','paid'),
        ('CANCELLED','cancelled'),
        ('DELIVERED','Delivered'),
        ('SHIPPED','Shipped'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('PAYPAL', 'PayPal'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE)
    total_price = models.FloatField(null=False)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='ordered')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    razorpay_order_id = models.CharField(max_length=150, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=150, blank=True, null=True)  # Add this field for payment ID
    razorpay_payment_signature=models.CharField(max_length=150, blank=True, null=True)
    message = models.TextField(null=True)
    tracking_no = models.CharField(max_length=150, null=True)
    order_date = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateTimeField(blank=True, null=True)
    
    
    

    def __str__(self):
        return f"{self.id, self.tracking_no}"
    def _str_(self):
        return f"{self.id}  {self.user.username}"

    def clean(self):
        if self.total_price == 0:
            raise ValidationError("Total price cannot be 0.")

    def save(self, *args, **kwargs):
        if not self.order_date:
            self.order_date = timezone.now()  # Set the order date to the current time if it's not set
        if not self.delivery_date:
            self.delivery_date = self.order_date + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_total_orders(cls):
        return cls.objects.count()
    @staticmethod
    def get_orders_count_week():
        return Order.objects.filter(order_date__gte=datetime.now()-timedelta(days=7)).count()
    @staticmethod
    def get_orders_count_month():
        return Order.objects.filter(order_date__gte=datetime.now()-timedelta(days=30)).count()
    @staticmethod
    def get_orders_count_day():
        return Order.objects.filter(order_date__gte=datetime.now()-timedelta(hours=24)).count()
    @staticmethod
    def get_total_revenue():
        total_revenue = Order.objects.aggregate(total_revenue=Sum('total_price'))['total_revenue']
        return total_revenue or 0
    @staticmethod
    def get_total_revenue_month():
        # Get the current month and year
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Calculate the start and end dates of the current month
        start_date = datetime(current_year, current_month, 1)
        end_date = start_date.replace(day=calendar.monthrange(current_year, current_month)[1])
        
        # Query the Order model to get the total revenue for the current month
        total_revenue = Order.objects.filter(order_date__date__range=(start_date, end_date)).aggregate(total_revenue=Sum('total_price'))['total_revenue']
        
        return total_revenue or 0
    @staticmethod
    def get_total_revenue_week():
        # Calculate the start and end dates of the current week
        end_date = datetime.now()
        start_date = end_date - timedelta(days=end_date.weekday())  # Get the start of the week
        
        # Query the Order model to get the total revenue for the current week
        total_revenue = Order.objects.filter(order_date__date__range=(start_date, end_date)).aggregate(total_revenue=Sum('total_price'))['total_revenue']
        
        return total_revenue or 0
    @staticmethod
    def get_total_revenue_day():
        # Calculate the start and end dates of the current day
        end_date = datetime.now()
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)  # Get the start of the day
        
        # Query the Order model to get the total revenue for the current day
        total_revenue = Order.objects.filter(order_date__range=(start_date, end_date)).aggregate(total_revenue=Sum('total_price'))['total_revenue']
        
        return total_revenue or 0






class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariantColor, on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    quantity = models.IntegerField(null=False)
    def __str__(self):
        return f"{self.order.id, self.order.tracking_no}"
         
    