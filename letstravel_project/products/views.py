from django.http import JsonResponse
from django.shortcuts import render

from admin_side.models import Product

# def home(request):
#     products = Product.objects.all()
#     return render(request, 'products/index.html', {'products': products})
# # Create your views here.

from django.core.paginator import Paginator

from admin_side.models import ProductImage
from admin_side.models import ColorVariant


# def home(request):
#     # Assuming 'Product' is your model and you want to fetch all products
#     all_products = Product.objects.all()

#     # Number of items per page
#     items_per_page = 10

#     # Create a Paginator object
#     paginator = Paginator(all_products, items_per_page)

#     # Get the current page number from the request's GET parameters
#     page_number = request.GET.get('page')

#     # Get the Page object for the requested page number
#     page = paginator.get_page(page_number)

#     context = {
#         'products': page,
#     }

#     return render(request, 'products/index.html', context)










def home(request, category_id=None):
    # Assuming 'Product' is your model and you want to fetch all products
    query = request.GET.get('query')
    products = Product.objects.select_related('category').prefetch_related(
        'variants__productvariant_set__productvariantcolor_set__productimage_set'
    )

    if category_id is not None:
        # Category ID is provided
        # Filter products based on the category ID
        all_products = all_products.filter(category_id=category_id)

    # Number of items per page
    items_per_page = 10

    # Create a Paginator object
    paginator = Paginator(products, items_per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the Page object for the requested page number
    page = paginator.get_page(page_number)

    context = {
        'products': page,
    }

    return render(request, 'products/index.html', context)





from django.shortcuts import render, get_object_or_404
from admin_side.models import Product, ProductVariant, ProductVariantColor


def productdetails(request, slug):
    product_variant_color = ProductVariantColor.objects.get(slug=slug)
    product = product_variant_color.product_variant.product
    # colors = ColorVariant.objects.filter(productvariantcolor__product_variant = product_variant_color.product_variant)
    # variants = product.variants.all()

    context = {
        'productvariantcolor': product_variant_color,
        'product': product,
        # 'color_variant': colors,
        # 'variants': variants,
        'selectedVariantId': product_variant_color.product_variant.id,
        'productVariantColorId': product_variant_color.id,
    }

    return render(request, 'products/product-detail.html', context)

    from django.http import JsonResponse

def getcolorids(request):
    variant_id = request.GET.get('variant_id')
    product_variant_color_ids = ProductVariantColor.objects.filter(product_variant_id=variant_id).values_list('id', flat=True)
    color_ids = list(product_variant_color_ids)
    return JsonResponse({'color_ids': color_ids})





def getcolorname(request):
    color_id = request.GET.get('color_id')

    try:
        product_variant_color = ProductVariantColor.objects.get(pk=color_id)
        
        color_name = product_variant_color.color_variant.color
        slug = product_variant_color.slug
        productvariantcolor_id = product_variant_color.pk


        response = {
            'color_name': color_name,
            'slug': slug,
            'productvariantcolor_id': productvariantcolor_id
        }
        return JsonResponse(response)
    except ProductVariantColor.DoesNotExist:
        return JsonResponse({'error': 'Product variant color not found'}, status=404)
