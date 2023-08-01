
from decimal import Decimal
import hashlib
import hmac
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import razorpay
from cart.models import Cart
from cart.models import CartItem
from discount.models import UserCoupon
from discount.models import CategoryOffer
from discount.models import UserCategoryOffer
from order.models import OrderItem
from order.models import Order
from userprofile.models import UserAddress
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.mail import send_mail
from razorpay import Client
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from .models import Order, OrderItem, Wallet
from userprofile.models import UserAddress
from .models import Transaction,Wallet
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wallet, Transaction       
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta     
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from django.db.models import Sum
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from .models import Order, OrderItem                                          
# Create your views here.


def cod(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    address_id = request.GET.get('address_id')
    user_add = UserAddress.objects.get(id=address_id, user=request.user)
    carts = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=carts)
    total_price = carts.total_price  
    if total_price == 0:
        messages.error(request, "Your cart is empty. Please add items to your cart before placing an order.")
        return redirect('shoppingcart')
        

    order = Order.objects.create(
    user=request.user,
    address=user_add,
    total_price=carts.total_price, 
    status='PENDING',
    payment_method='Cash On Delivery',
        )

    user_coupons = UserCoupon.objects.filter(user=request.user, used=False)
    for user_coupon in user_coupons:
                user_coupon.used = True
                user_coupon.order = order
                user_coupon.save()

    for cart_item in items:
                    # Check if the cart item's product variant color is on offer
                    if cart_item.product_variant_color.on_offer:
                        # Increment claimed by 1 and update the total amount claimed
                        product_variant_color = cart_item.product_variant_color
                        category_offer = CategoryOffer.objects.get(category=product_variant_color.category, is_active=True)
                        category_offer.total_claimed += 1
                        discounted_amount = product_variant_color.price - product_variant_color.offer_price
                        category_offer.total_amount_claimed += discounted_amount
                        category_offer.save()       
             
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

def place_order(request, add_user_id):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    else:   
         order = Order.objects.filter(user=request.user).latest('id')
         order_items = order.orderitem_set.all()
         context = {
             'order': order,
             'order_items': order_items
         }
         return render(request, 'order/prepaysuccess.html', context)

def ordertable(request):
    
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    else:
        order = Order.objects.filter(user=request.user).order_by('-order_date')
        paginator = Paginator(order, 10)  # Set the number of orders to display per page
    
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    
        context = {
        'page_obj': page_obj
         }
        return render(request, 'order/ordertable.html', context)

def order_view(request,order_id):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    else:
         orderss = Order.objects.get(id=order_id)
         address = orderss.address
         view_order = OrderItem.objects.filter(order=orderss)
         context ={
             'view_order':view_order,
             'order': orderss,
             'address':address,
         }
    return render(request,"order/order_view.html",context)

#-----------------------------Cancel the order from user side------------------------------------------------

def cancel_orders(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    
    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order)
    
    if order.status == 'PENDING' or order.status == 'Payment Recieved':
        # Calculate the total amount to be credited to the wallet
        if order.payment_method == 'RAZORPAY' or order.payment_method == 'WALLET PAY':
            total_amount_to_credit = Decimal(order.total_price)
            
            # Update the wallet balance
            
            wallet = Wallet.objects.get(user=order.user)
            wallet.balance += total_amount_to_credit
            wallet.save()
                
                # Create a wallet transaction record for the credit
            transaction = Transaction.objects.create(
                    wallet=wallet,
                    amount=total_amount_to_credit,
                    is_credit=True,
                    is_order_cancellation=True
                )
            user_coupons = UserCoupon.objects.filter(order=order)
        
            for user_coupon in user_coupons:
                try:
                    # Get the coupon associated with the user_coupon
                    coupon = user_coupon.coupon
                    
                    # Decrement the total claimed and total amount claimed for the coupon
                    coupon.total_claimed = (coupon.total_claimed or 0) - 1
                    coupon.total_amount_claimed = (coupon.total_amount_claimed or 0) - user_coupon.amount_discounted
                    coupon.save()
                    user_coupon.applied = False
                    user_coupon.used = False
                    user_coupon.amount_discounted = 0
                    user_coupon.order = None
                    user_coupon.save()
                except UserCoupon.DoesNotExist:
                    pass   
    # Update the order status to 'CANCELLED'
        order.status = 'CANCELLED'
        order.save()

        # Send email notification to the user about the cancellation
        send_mail(
            'Your order has been cancelled',
            f"Dear {order.user.username},\n\nYour order (ID: {order.id}) has been successfully cancelled. ",
            'your_email@example.com',  # Replace with your email address
            [order.user.email],
            fail_silently=False,
        )        
        # Restore the stock for each product variant in the order
        for order_item in items:
            variant = order_item.product
            variant.stock += order_item.quantity
            variant.save()
                    
        return redirect('ordertable')

def pay_now(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')  
    address_id = request.GET.get('address_id')
    
    user_add = UserAddress.objects.get(id=address_id, user=request.user)
    
    carts = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=carts)
    total_price = carts.total_price

    if total_price == 0:
        messages.error(request, "Your cart is empty. Please add items to your cart before placing an order.")
        return redirect('shoppingcart')     
    context ={
        'address_id':address_id,
        'user_add': user_add,
         'carts': carts,
         'items': items,
         'total_price': total_price,
    }
    return render(request,"order/paynow.html",context)

def online_payment_order(request,user_add_id):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    if request.method == 'POST':
        payment_id = request.POST.getlist('payment_id')[0]
        orderId = request.POST.getlist('orderId')[0]
        signature = request.POST.getlist('signature')[0]
        
        user_add = UserAddress.objects.get(id=user_add_id, user=request.user)
        carts = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=carts)
        total_price = carts.total_price  

        order = Order.objects.create(
        user=request.user,
        address=user_add,
        total_price_before_discount = carts.total_price_before_discount,
        total_price=carts.total_price, 
        status='Payment Recieved',
        payment_method='RAZORPAY',
        razorpay_payment_id=payment_id,
        razorpay_payment_signature=signature,
        razorpay_order_id = orderId,
        )

        user_coupons = UserCoupon.objects.filter(user=request.user, used=False)
        for user_coupon in user_coupons:
                user_coupon.used = True
                user_coupon.order = order
                user_coupon.save()
        
        for cart_item in items:
                    # Check if the cart item's product variant color is on offer
                    if cart_item.product_variant_color.on_offer:
                        # Increment claimed by 1 and update the total amount claimed
                        product_variant_color = cart_item.product_variant_color
                        category_offer = CategoryOffer.objects.get(category=product_variant_color.category, is_active=True)
                        category_offer.total_claimed += 1
                        discounted_amount = product_variant_color.price - product_variant_color.offer_price
                        category_offer.total_amount_claimed += discounted_amount
                        category_offer.save()

                    #     user_category_offer = UserCategoryOffer.objects.create(
                    #     user=Cart.user,
                    #     category_offer=category_offer,
                    #     is_claimed=True,
                    #     claimed_date=datetime.now(),  # Update this with the actual date and time of the claim
                    #     discounted_amount=discounted_amount
                    # )  

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
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
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
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
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
    



def pay_using_wallet(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        carts = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=carts)
        total_amount_to_pay =carts.total_price,   # Replace this with the actual total amount to be paid
        user_wallet = Wallet.objects.get(user=request.user)
        user_add = UserAddress.objects.get(id=address_id, user=request.user)
        
        if carts.total_price==0:
             return redirect('home')

        if user_wallet.balance >= carts.total_price:
            # Sufficient balance in the wallet, proceed with the payment
            try:
                # Deduct the amount from the wallet balance
                user_wallet.balance -= total_amount_to_pay
                user_wallet.save()

                # Create a transaction record for the payment
                transaction = Transaction.objects.create(
                    wallet=user_wallet,
                    amount=total_amount_to_pay,
                    is_credit=False,  # Payment is a debit from the wallet
                    is_order_cancellation=False,  # Set these values based on your needs
                    is_order_return=False,
                )

                order = Order.objects.create(
                user=request.user,
                address=user_add,
                total_price=carts.total_price, 
                status='Payment Recieved',
                payment_method='WALLET PAY',
                    )

                user_coupons = UserCoupon.objects.filter(user=request.user, used=False)
                for user_coupon in user_coupons:
                            user_coupon.used = True
                            user_coupon.order = order
                            user_coupon.save()

                for cart_item in items:
                    # Check if the cart item's product variant color is on offer
                    if cart_item.product_variant_color.on_offer:
                        # Increment claimed by 1 and update the total amount claimed
                        product_variant_color = cart_item.product_variant_color
                        category_offer = CategoryOffer.objects.get(category=product_variant_color.category, is_active=True)
                        category_offer.total_claimed += 1
                        discounted_amount = product_variant_color.price - product_variant_color.offer_price
                        category_offer.total_amount_claimed += discounted_amount
                        category_offer.save()     
                        
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
                # Perform other tasks related to the successful wallet payment
                # For example, mark the order as paid, update the order status, etc.
                messages.success(request, 'Payment successful! Your order has been placed.')
                return redirect('order_success')  # Replace 'ordertable' with the URL name for your order table page
            except Exception as e:
                # Handle any exceptions that might occur during the payment process
                # For example, if there is an error during transaction creation, you may need to revert the wallet balance
                # and handle the exception appropriately
                messages.error(request, 'Payment failed! Please try again later.')
                return redirect('shoppingcart')  # Replace 'ordertable' with the URL name for your order table page
        else:
            # Insufficient balance in the wallet
            messages.error(request, 'Payment failed! Insufficient balance in your wallet. Add money to wallet. or select another payment option')
            return redirect('shoppingcart')  # Replace 'ordertable' with the URL name for your order table page


def view_wallets(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    wallets = Wallet.objects.all()
    return render(request, 'adminpages/viewwallet.html', {'wallets': wallets})
# views.py
from django.shortcuts import render
from .models import Order


from django.shortcuts import render
from .models import Order

def generate_invoice(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    order = Order.objects.get(pk=order_id)

    # Calculate the total for each order item
    for order_item in order.orderitem_set.all():
        order_item.total = order_item.price * order_item.quantity

    context = {
        'order': order,
        'order_items': order.orderitem_set.all(),  # Pass the order items with totals to the template
    }

    return render(request, 'order/invoice.html', context)





def quantize_decimal(value):
    return value.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

def download_sales_report(request):
    if request.method == 'POST':
         
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

    # Convert the start_date and end_date strings to datetime objects if needed
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Validate end date is after start date
    if start_date and end_date and end_date < start_date:
        # Set the end date to be the same as the start date
        end_date = start_date

    today = datetime.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Fetch orders within the selected time frame
    if start_date and end_date:
        orders_within_time_frame = Order.objects.filter(order_date__date__range=[start_date, end_date])
    else:
        # If no start_date and end_date are selected, fetch all orders
        orders_within_time_frame = Order.objects.all()


    today = datetime.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Today's totals
    today_orders = Order.objects.filter(order_date__date=today)
    order_count_today = today_orders.count()
    total_price_today = today_orders.aggregate(Sum('total_price'))['total_price__sum']
    total_price_today = Decimal(str(total_price_today))
    total_price_today = quantize_decimal(total_price_today)

    # Weekly totals
    week_orders = Order.objects.filter(order_date__date__range=[week_ago, today])
    order_count_week = week_orders.count()
    total_price_week = week_orders.aggregate(Sum('total_price'))['total_price__sum']
    total_price_week = Decimal(str(total_price_week))
    total_price_week = quantize_decimal(total_price_week)

    # Monthly totals
    month_orders = Order.objects.filter(order_date__date__range=[month_ago, today])
    order_count_month = month_orders.count()
    total_price_month = month_orders.aggregate(Sum('total_price'))['total_price__sum']
    total_price_month = Decimal(str(total_price_month))
    total_price_month = quantize_decimal(total_price_month)


    context = {
        'order_count_today': order_count_today,
        'total_price_today': total_price_today,
        'order_count_week': order_count_week,
        'total_price_week': total_price_week,
        'order_count_month': order_count_month,
        'total_price_month': total_price_month,
        'orders': orders_within_time_frame,
        'start_date': start_date,
        'end_date': end_date,
        
    }

    # Render the HTML content using the 'sales.html' template and the provided context
    html_content = render_to_string('order/salesreport.html', context)

    # Set the response content type as 'application/pdf' to indicate that it's a PDF file
    response = HttpResponse(content_type='application/pdf')

    # Set the filename for the downloaded file
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Generate the PDF content from the HTML using xhtml2pdf
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), response)

    if pdf.err:
        return HttpResponse('Error generating PDF', status=500)

    return response



def download_invoice(request,order_id):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    else:
         orderss = Order.objects.get(id=order_id)
         address = orderss.address
         view_order = OrderItem.objects.filter(order=orderss)
         context ={
             'view_order':view_order,
             'order': orderss,
             'address':address,
         }
    # Render the HTML content using the 'sales.html' template and the provided context
    html_content = render_to_string('order/invoice.html', context)

    # Set the response content type as 'application/pdf' to indicate that it's a PDF file
    response = HttpResponse(content_type='application/pdf')

    # Set the filename for the downloaded file
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    # Generate the PDF content from the HTML using xhtml2pdf
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), response)

    if pdf.err:
        return HttpResponse('Error generating PDF', status=500)

    return response
