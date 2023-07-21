from admin_side.models import ProductVariantColor
from admin_side.models import Category

def get_product_variant_colors_by_category(category_id):
    try:
        # Step 1: Filter ProductVariantColor instances by the given category_id
        product_variant_colors = ProductVariantColor.objects.filter(category_id=category_id)
        return product_variant_colors
    except Category.DoesNotExist:
        # Handle the case when the category with the given ID does not exist
        return []