from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from cart.models import Cart
from cart.models import CartItem
from order.models import OrderItem
from order.models import Order
from userprofile.models import UserAddress
from django.db import IntegrityError
# Create your views here.


def checkout(request, address_id):
    try:
        user_add = UserAddress.objects.get(id=address_id, user=request.user)
    except UserAddress.DoesNotExist:
        return HttpResponse('Address not found.')  
    carts = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=carts)
    total_price = carts.total_price  
    if total_price == 0:
        return HttpResponse('Cart is empty.')

    order = Order.objects.create(
    user=request.user,
    address=user_add,
    total_price=carts.total_price, 
    status='PENDING',
    payment_method='PAYPAL',
        )     
             
    for cart_item in items:
            OrderItem.objects.create(
            order=order,
            product=cart_item.product_variant_color,
            price=cart_item.price,
            quantity=cart_item.quantity
            # Set other fields as necessary
        )
    items.delete()  
    # return render(request, "order/checkout.html", {"user_add": user_add, "carts": carts})
    return render(request, "order/checkout.html", {"user_add": user_add, "carts": carts})



def place_order(request,add_user_id):    
     last_order = Order.objects.filter(user=request.user).latest('id')
     
     context={
          'last_order':last_order
     }
     return render(request,'order/order_place.html',context)


def ordertable(request):
    order = Order.objects.filter(user=request.user)
    context = {
        'order':order
    }
    return render(request,'order/ordertable.html',context)

def order_view(request,order_id):
    orderss = Order.objects.get(id=order_id)
    view_order = OrderItem.objects.filter(order=orderss)
    context ={
        'view_order':view_order
    }
    return render(request,"order/order_view.html",context)


def cancel_orders(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'PAID' and order.status != 'CANCELLED':
            # Update the payment status to 'CANCELLED'
            order.status = 'CANCELLED'
            order.save()
    return redirect('ordertable')