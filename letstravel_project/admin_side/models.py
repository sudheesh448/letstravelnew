# from django.db import models
# from django.contrib.auth.models import User



# class Category(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()

# class Variant(models.Model):
#     name = models.CharField(max_length=100)
#     category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='variants')

#     def __str__(self):
#         return self.name


# class ColorVariant(models.Model):
#     color = models.CharField(max_length=50)

#     def __str__(self):
#         return self.color




# class Product(models.Model):
#     product_code = models.CharField(max_length=50, unique=True, blank=False)
#     name = models.CharField(max_length=200)
#     tags = models.CharField(max_length=200)
#     quantity_left = models.PositiveIntegerField()
#     description = models.TextField()
#     color_variant = models.ForeignKey(ColorVariant, on_delete=models.PROTECT, related_name='products')
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     product_deleted = models.BooleanField(default=False)
#     product_deleted_at = models.DateTimeField(null=True, blank=True)
#     category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
#     variants = models.ManyToManyField(Variant, related_name='products')

#     def __str__(self):
#         return self.name



# class ProductImage(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
#     image = models.ImageField(upload_to='product_images/')
#     Product_deleted_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return f"Image for {self.product.name}"


# class Rating(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
#     customer = models.ForeignKey(User, on_delete=models.CASCADE)
#     rating = models.PositiveIntegerField()

#     def __str__(self):
#         return f"Rating: {self.rating} for {self.product.name} by {self.customer.username}"


# class Review(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
#     customer = models.ForeignKey(User, on_delete=models.CASCADE)
#     review = models.TextField()

#     def __str__(self):
#         return f"Review for {self.product.name} by {self.customer.username}"
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from psycopg import Transaction
import random
import string


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Variant(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='variants')

    def __str__(self):
        return self.name

class ColorVariant(models.Model):
    color = models.CharField(max_length=50)
    def __str__(self):
        return self.color

class Product(models.Model):
    name = models.CharField(max_length=200)
    product_code = models.CharField(max_length=50, unique=True, blank=False)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    slug = models.SlugField(unique=True)
    product_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    variants = models.ManyToManyField(Variant, through='ProductVariant')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} - {self.variant.name}"
    
    class Meta:
        unique_together = ('product', 'variant')



class ProductVariantColor(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    stock = models.PositiveIntegerField()
    variant_deleted = models.BooleanField(default=False)
    on_offer = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # New field for the category

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.product_variant}-{self.color_variant}")
        super(ProductVariantColor, self).save(*args, **kwargs)

    
    def get_absolute_url(self):
        return reverse("productdetails", kwargs={"slug": self.slug})
    class Meta:
        unique_together = ('product_variant', 'color_variant')
    def __str__(self):
        return f"{self.product_variant.product.name} - {self.product_variant.variant.name} - {self.color_variant.color}"


class ProductImage(models.Model):
    product_variant_color = models.ForeignKey(ProductVariantColor, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product_variant_color}"




class PhoneNumber(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    total_cliamed = models.DecimalField(max_digits=5, decimal_places=0,blank=True, null=True)
    total_amount_cliamed = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True)
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')

    def __str__(self):
        return self.phone_number

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_referral_code():
        letters = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(letters) for _ in range(6))
        return code 

@receiver(post_save, sender=User)
def create_phone_number(sender, instance, created, **kwargs):
    if created:
        phone_number = PhoneNumber.objects.create(user=instance)


@receiver(post_save, sender=PhoneNumber)
def update_referrer_wallet(sender, instance, created, **kwargs):
    from order.models import Wallet
    from order.models import Transaction
    from django.core.mail import send_mail
    if  instance.referred_by:
        referrer = instance.referred_by
        email=referrer.email
        try:
            wallet = Wallet.objects.get(user=referrer)
            wallet.balance += Decimal('100.00')
            wallet.save()
            Transaction.objects.create(wallet=wallet, amount=Decimal('100.00'), is_credit=True)

            send_mail(
                'Wallet credit',
                f'Your wallet have a credit of Rs 100 for refering {instance.user.email}',
                'letstravelllp@gmail.com',
                [email],
                fail_silently=False,
            )
        except Wallet.DoesNotExist:
            # Handle the case when the referrer doesn't have a wallet yet
            pass