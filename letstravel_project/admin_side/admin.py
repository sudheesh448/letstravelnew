
from django.contrib import admin
from admin_side.models import Category, ColorVariant, Product,Variant,ProductImage,ProductVariant,ProductVariantColor,PhoneNumber

admin.site.register(Category)

admin.site.register(Variant)
admin.site.register(ProductImage)
admin.site.register(ColorVariant)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductVariantColor)
admin.site.register(PhoneNumber)



# Register your models here.
