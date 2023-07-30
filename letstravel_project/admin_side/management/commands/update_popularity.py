# update_popularity.py
from django.core.management.base import BaseCommand
from admin_side.models import ProductVariantColor
from order.models import  OrderItem

class Command(BaseCommand):
    help = 'Update popularity for ProductVariantColor instances'

    def handle(self, *args, **kwargs):
        # Get all ProductVariantColor instances
        product_variant_colors = ProductVariantColor.objects.all()

        for pvc in product_variant_colors:
            # Calculate popularity by counting the occurrences in the OrderItem table
            pvc.popularity = OrderItem.objects.filter(product=pvc).count()
            pvc.save()

        self.stdout.write(self.style.SUCCESS('Popularity updated successfully.'))
