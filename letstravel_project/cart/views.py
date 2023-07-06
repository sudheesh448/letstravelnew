from django.shortcuts import redirect, render

# Create your views here.
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from admin_side.models import ProductVariantColor
from cart.models import Cart,CartItem
from cart.models import CartItem
from cart import models


def addtocart(request):
    print("hiii")

    if request.method == 'POST' :
        productvariantcolor_id = request.POST.get('product_variant_color_id')
        print(productvariantcolor_id)

        # Retrieve the product based on the provided ID
        productvariantcolor = get_object_or_404(ProductVariantColor, id=productvariantcolor_id)

        print(productvariantcolor_id)

        # Assuming the user is authenticated, retrieve their cart or create a new one
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the product is already in the cart
        cart_item = cart.items.filter(product_variant_color=productvariantcolor).first()
        
        print(productvariantcolor_id)

        if cart_item:
            # Increment the quantity if the product is already in the cart
            cart_item.quantity += 1
            cart_item.save()
        else:
            # Create a new cart item if the product is not yet in the cart
            CartItem.objects.create(cart=cart, product_variant_color=productvariantcolor, price=productvariantcolor.price, subtotal=productvariantcolor.price)
        return JsonResponse({'message': 'Product added to cart successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def shoppingcart(request):
    cart = Cart.objects.get(user=request.user)
    print(cart)
    context = {
        'cart': cart,
    }
    return render(request, 'cart/shop_cart.html',context)


def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        print(item_id)
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()
        
        
        return redirect('shoppingcart')

    return render(request, 'cart/shop_cart.html')



from django.http import JsonResponse
from .models import CartItem

def decrement_quantity(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')

        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Quantity cannot be less than 1'})
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order item does not exist'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

def increment_quantity(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')

        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            cart_item.quantity += 1
            cart_item.save()
            return JsonResponse({'success': True})
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order item does not exist'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
