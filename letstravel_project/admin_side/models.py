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


from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse

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
    stock = models.PositiveIntegerField()
    variant_deleted = models.BooleanField(default=False)

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
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.phone_number