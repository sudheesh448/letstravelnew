from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from admin_side.models import ProductVariantColor
from cart.models import Cart,CartItem
from cart.models import CartItem
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect
from cart.models import CartItem
from decimal import Decimal
from discount.models import Coupon,UserCoupon


def addtocart(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    if request.method == 'POST' :
        productvariantcolor_id = request.POST.get('product_variant_color_id')
        # Retrieve the product based on the provided ID
        productvariantcolor = get_object_or_404(ProductVariantColor, id=productvariantcolor_id)
        # Assuming the user is authenticated, retrieve their cart or create a new one
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Check if the product is already in the cart
        cart_item = cart.items.filter(product_variant_color=productvariantcolor).first() 
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
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # If the cart was just created, you may want to set some default values
        if created:
            cart.save()  # Save the newly created cart to the database
        cart_items = cart.items.order_by('price')  # Order the items by price
    else:
        messages.warning(request, 'Sign in required to continue.')
        return redirect('signin')

    

    # Get the applied coupons for the user with the condition applied=True and used=False
    applied_coupons = UserCoupon.objects.filter(user=request.user, applied=True, used=False)

    context = {
        'cart': cart,
        'cart_items': cart_items,  # Pass the ordered cart items to the template
        'Cart_item_id': cart.id,
        'applied_coupons': applied_coupons,  # Pass the applied coupons
    }
    return render(request, 'cart/shop_cart.html', context)

def remove_from_cart(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
       
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()  
        return redirect('shoppingcart')
    return render(request, 'cart/shop_cart.html')

def increment_quantity(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    cart_item_id = request.POST.get('item_id')
    
    cart_item = CartItem.objects.get(id=cart_item_id)
    
    stock = cart_item.product_variant_color.stock
    if cart_item.quantity < stock:
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.error(request, 'The quantity cannot exceed the available stock.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def decrement_quantity(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    cart_item_id = request.POST.get('item_id')
    cart_item = CartItem.objects.get(id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        messages.error(request, 'Minimum quantity required-1')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def apply_coupon(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon')
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            user = request.user
            cart = Cart.objects.get(user=user)

            # Check if the cart meets the minimum order amount
            if cart.total_price_before_discount < coupon.min_order_total:
                messages.error(request, f'The minimum order amount to use this coupon is ${coupon.min_order_total}.')
            else:
                # Check if the coupon is already used by the user
                user_coupon = UserCoupon.objects.filter(user=user, coupon=coupon).first()
                if user_coupon:
                    if user_coupon.used:
                        messages.error(request, 'This coupon has already been used.')
                    elif user_coupon.applied:
                        messages.error(request, 'This coupon has already been applied.')
                    else:
                        # Update the UserCoupon instance as applied and calculate the discount
                        user_coupon.applied = True
                        if coupon.is_percentage:
                            discount_amount = min(cart.total_price * (coupon.discount / 100), coupon.max_discount_amount)
                        else:
                            discount_amount = min(coupon.discount, coupon.max_discount_amount)
                        user_coupon.amount_discounted = discount_amount
                        user_coupon.save()
                        # Apply the discount to the cart
                        cart.total_price -= discount_amount
                        cart.save()
                        messages.success(request, f'Coupon applied successfully. Discount: ${discount_amount}')
                else:
                    # Create a new UserCoupon instance and apply the discount to the cart
                    discount_amount = 0
                    if coupon.is_percentage:
                        discount_amount = min(cart.total_price_before_discount * (coupon.discount / 100), coupon.max_discount_amount)
                    else:
                        discount_amount = min(coupon.discount, coupon.max_discount_amount)
                    UserCoupon.objects.create(user=user, coupon=coupon, applied=True, amount_discounted=discount_amount)
                    cart.total_price -= discount_amount
                    cart.save()
                    messages.success(request, f'Coupon applied successfully. Discount: ${discount_amount}')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
    return redirect('shoppingcart')



