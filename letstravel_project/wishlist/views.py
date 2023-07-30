from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import Wishlist, WishlistItem, ProductVariantColor


# views.py
from django.http import JsonResponse

def add_to_wishlist(request):
    if request.method == 'POST' :
        product_id = request.POST.get('product_id')
        user = request.user

        # Find the product_variant_color using the product_id (You'll need to implement this part)
        product_variant_color = ProductVariantColor.objects.get(id=product_id)

        # Get or create the user's wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=user)

        # Add the product to the wishlist
        wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product_variant_color=product_variant_color)

        # Return a success response
        return JsonResponse({'message': 'Product added to wishlist successfully.'})

    # Return an error response if the request is not AJAX or not POST
    return JsonResponse({'error': 'Invalid request.'}, status=400)


from django.views.decorators.http import require_POST
@require_POST
def remove_from_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    product_id = request.POST.get('product_id')

    try:
        user = request.user
        wishlist = Wishlist.objects.get(user=user)
        wishlist_item = WishlistItem.objects.get(wishlist=wishlist, product_variant_color_id=product_id)
        wishlist_item.delete()
        return JsonResponse({'removed': True})
    except Wishlist.DoesNotExist:
        return JsonResponse({'error': 'Wishlist not found'}, status=404)
    except WishlistItem.DoesNotExist:
        return JsonResponse({'error': 'Product not found in wishlist'}, status=404)


def view_wishlist(request):
    if not request.user.is_authenticated:
        return render(request, 'wishlist/not_authenticated.html')

    user = request.user
    
    # Fetch the user's wishlist or create one if it doesn't exist
    wishlist, created = Wishlist.objects.get_or_create(user=user)

    # Fetch the wishlist items for the user
    wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
    wishlist_items_product_variant_color_ids = list(wishlist_items.values_list('product_variant_color__id', flat=True))
    products = [item.product_variant_color for item in wishlist_items]

    context = {
        'wishlist_items_product_variant_color_ids': wishlist_items_product_variant_color_ids,
        'products':products
    }

    return render(request, 'products/wishlist.html', context)

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ProductVariantColor, Wishlist, WishlistItem


def add_to_wishlist_product_detail(request):
    if request.user.is_authenticated:
        product_variant_color_id = request.POST.get('product_variant_color_id')

        try:
            product_variant_color = ProductVariantColor.objects.get(id=product_variant_color_id)
        except ProductVariantColor.DoesNotExist:
            return JsonResponse({'error': 'Invalid product variant color ID.'}, status=400)

        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product_variant_color=product_variant_color)

        return JsonResponse({'message': 'Product added to wishlist successfully.'})
    else:
        return JsonResponse({'error': 'User must be logged in to add products to the wishlist.'}, status=403)


