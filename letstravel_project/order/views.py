import hashlib
import hmac
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import razorpay
from cart.models import Cart
from cart.models import CartItem
from order.models import OrderItem
from order.models import Order
from userprofile.models import UserAddress
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.mail import send_mail                                                      
# Create your views here.


def cod(request):
    address_id = request.GET.get('address_id')
    user_add = UserAddress.objects.get(id=address_id, user=request.user)
    
    carts = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=carts)
    total_price = carts.total_price  
    # if total_price == 0:
    #     return HttpResponse('Cart is empty.')

    order = Order.objects.create(
    user=request.user,
    address=user_add,
    total_price=carts.total_price, 
    status='PENDING',
    payment_method='Cash On Delivery',
        )     
             
    for cart_item in items:
            OrderItem.objects.create(
            order=order,
            product=cart_item.product_variant_color,
            price=cart_item.price,
            quantity=cart_item.quantity
            # Set other fields as necessary
        )
            variant = cart_item.product_variant_color   
            variant.stock -= cart_item.quantity
            variant.save()
    items.delete()  
    # return render(request, "order/checkout.html", {"user_add": user_add, "carts": carts})
    return render(request, "order/checkout.html", {"user_add": user_add, "carts": carts})


from razorpay import Client



def place_order(request, add_user_id):    
    order = Order.objects.filter(user=request.user).latest('id')
    order_items = order.orderitem_set.all()

    context = {
        'order': order,
        'order_items': order_items
    }

    return render(request, 'order/prepaysuccess.html', context)


from django.core.paginator import Paginator
def ordertable(request):
    order = Order.objects.filter(user=request.user).order_by('-order_date')
    paginator = Paginator(order, 10)  # Set the number of orders to display per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj
    }
    return render(request, 'order/ordertable.html', context)

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

            send_mail(
                'Your order hasbeen cancelled',
                f"Dear {order.user.username},\n\nYour order (ID: {order.id}) has been successfully cancelled. ",
                'your_email@example.com',  # Replace with your email address
                [order.user.email],
                fail_silently=False,
            )
    return redirect('ordertable')





def pay_now(request):  
    address_id = request.GET.get('address_id')
    print(address_id)
    user_add = UserAddress.objects.get(id=address_id, user=request.user)
    print(user_add)
    carts = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=carts)
    total_price = carts.total_price     
    context ={
        'address_id':address_id,
        'user_add': user_add,
         'carts': carts,
         'items': items,
         'total_price': total_price,
    }
    return render(request,"order/paynow.html",context)



def online_payment_order(request,user_add_id):
    if request.method == 'POST':
        payment_id = request.POST.getlist('payment_id')[0]
        orderId = request.POST.getlist('orderId')[0]
        signature = request.POST.getlist('signature')[0]



        
        user_add = UserAddress.objects.get(id=user_add_id, user=request.user)
        carts = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=carts)
        total_price = carts.total_price  

        print("-------------------------------------------------")
        print(payment_id)
        print(signature)
        print(orderId)
        print("-------------------------------------------------")
    
    
        order = Order.objects.create(
        user=request.user,
        address=user_add,
        total_price=carts.total_price, 
        status='Payment Recieved',
        payment_method='RAZORPAY',
        razorpay_payment_id=payment_id,
        razorpay_payment_signature=signature,
        razorpay_order_id = orderId,
        )  

        for cart_item in items:
            OrderItem.objects.create(
            order=order,
            product=cart_item.product_variant_color,
            price=cart_item.price,
            quantity=cart_item.quantity
            # Set other fields as necessary
        )
            variant = cart_item.product_variant_color   
            variant.stock -= cart_item.quantity
            variant.save()
        items.delete()  
      
        return JsonResponse({'message': 'Order placed successfully'})
    else:
        # Handle invalid request method (GET, etc.)
        return JsonResponse({'error': 'Invalid request method'})



def initiate_payment(request):
    if request.method == 'POST':
        # Retrieve the total price and other details from the backend
        cartss = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=cartss)
        # total_price = sum(item.price * item.quantity for item in items)
        total_price =1
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        payment = client.order.create({'amount': int(total_price * 100), 'currency': 'INR', 'payment_capture': 1})
    
        response_data = {
            'order_id': payment['id'],
            'amount': payment['amount'],
            'currency': payment['currency'],
            'key': settings.RAZOR_KEY_ID
        }
        return JsonResponse(response_data)

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request method'})

def order_success(request):
    payment_id = request.GET.get('payment_id')

    # Retrieve the Order and OrderItem objects based on the payment_id
    order_and_items = Order.objects.filter(
        Q(razorpay_payment_id=payment_id) | Q(orderitem__order__razorpay_payment_id=payment_id)
    ).prefetch_related('orderitem_set')

    # Access the Order and OrderItem objects
    order = order_and_items.first()
    order_items = order.orderitem_set.all()

    context = {
        'payment_id': payment_id,
        'order': order,
        'order_items': order_items
    }

    return render(request, 'order/prepaysuccess.html', context)