from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import cache_control,never_cache
from psycopg import IntegrityError
from admin_side.forms import ImageForm
from order.models import OrderItem
from order.models import Order
from .models import Category, ColorVariant
from .models import Category, Variant, Product, ProductImage
from django.core.paginator import Paginator
from .models import Product, ProductVariant, ProductVariantColor, ProductImage
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product
from .models import Category, Variant
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .models import Product, ProductVariant, ProductVariantColor
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.db import IntegrityError
from .models import Product, Variant, ProductVariant, ProductVariantColor



def add_category(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                if request.method == 'POST':
                    name = request.POST.get('name')
                    description = request.POST.get('description')
                    # Create a new category object
                    category = Category.objects.create(name=name, description=description)
                    # Redirect to a success page or another view
                    request.session['last_category_key'] = category.pk
                
                    return redirect('addvariants')  
                return render(request, 'adminpages/addcategory.html')
            
    else:
            return redirect('adminlogin')   


def addvariants(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                category_id = request.session.get('last_category_key')    
                if category_id:
                    category = Category.objects.get(id=category_id)
                    name = category.name
                else:
                    # Handle the case when category_id is not found or category does not exist
                    return redirect('dashboard')
                if request.method == 'POST':
                    variant_names = request.POST.getlist('variant[]')
                    for variant_name in variant_names:
                        variant = Variant(name=variant_name, category=category)
                        variant.save()
                    return redirect('dashboard')
                return render(request, 'adminpages/addvariants.html', {'category': name})
    else:
            return redirect('adminlogin')  


def category_view(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                search_query = request.GET.get('search')
                category_list = Category.objects.prefetch_related('variants').all()
                if search_query:
                    category_list = category_list.filter(Q(name__icontains=search_query))
                paginator = Paginator(category_list, 10)  # Show 10 categories per page
                page_number = request.GET.get('page')
                categories = paginator.get_page(page_number) 
                return render(request, 'adminpages/categorylist.html', {'categories': categories, 'search_query': search_query})
    else:
            return redirect('adminlogin')



def category_update(request, category_id):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                category = get_object_or_404(Category, pk=category_id)
                
                if request.method == 'POST':
                    # Update Category fields
                    category.name = request.POST.get('name')
                    category.description = request.POST.get('description')
                    category.save()
                    
                    # Delete Variants if necessary
                    variant_ids = request.POST.getlist('delete_variant')
                    Variant.objects.filter(id__in=variant_ids, category=category).delete()
                    request.session['last_category_key'] = category.pk
                    return redirect('addvariants')
                
                variants = category.variants.all()
                return render(request, 'adminpages/category_update.html', {'category': category, 'variants': variants})
    else:
            return redirect('adminlogin')            





def productlist(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                query = request.GET.get('query')
                products = Product.objects.select_related('category').prefetch_related(
                    'variants__productvariant_set__productvariantcolor_set__productimage_set'
                )
                if query:
                    products = products.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
                paginator = Paginator(products, 10)  # Show 10 products per page
                page_number = request.GET.get('page')
                page_products = paginator.get_page(page_number)
                context = {
                    'products': page_products,
                    'query': query
                }
                return render(request, 'adminpages/productlist.html', context)
            else:
                return redirect('adminlogin') 


def ordertableadmin(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                search_query = request.GET.get('q')
                order_list = Order.objects.order_by('-id')
                if search_query:
                    order_list = order_list.filter(
                        Q(id__icontains=search_query) |
                        Q(user__username__icontains=search_query) |
                        Q(status__icontains=search_query) |
                        Q(payment_method__icontains=search_query)
                    )
                paginator = Paginator(order_list, 10)  # Show 10 orders per page
                page_number = request.GET.get('page')
                orders = paginator.get_page(page_number)
                context = {
                    'orders': orders,
                    'search_query': search_query
                }
                return render(request, 'adminpages/orders.html', context)
            else:
                return redirect('adminlogin') 


def order_viewadmin(request, order_id):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                order = get_object_or_404(Order, id=order_id)
                view_order = OrderItem.objects.filter(order=order)
                user = order.user
                address = order.address

                context = {
                    'order': order,
                    'view_order': view_order,
                    'user': user,
                    'address': address,
                }
                return render(request, "adminpages/order_viewadmin.html", context)
            else:
                return redirect('adminlogin') 


def Shipped_order(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'PAID' and order.status != 'CANCELLED':
            # Update the payment status to 'CANCELLED'
            order.status = 'SHIPPED'
            order.save()
    return redirect('ordertableadmin')

def Delivered_order(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'PAID' and order.status != 'CANCELLED' and order.status == 'SHIPPED':
            # Update the payment status to 'CANCELLED'
            order.status = 'DELIVERED'
            order.save()
    return redirect('ordertableadmin')


def viewproduct(request, product_id):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                product = get_object_or_404(Product, pk=product_id)

                if request.method == 'POST':
                    name = request.POST.get('name')
                    description = request.POST.get('description') 
                    product.name = name
                    product.description = description
                    product.save()   
                category = product.category
                variants = Variant.objects.filter(category_id=category.pk)
                colors = ColorVariant.objects.all()
                request.session['last_product_key'] = product.pk
                
                context = {
                    'product': product,
                    'variants':variants,
                    'category':category,
                    'colors':colors
                }
                return render(request, 'adminpages/viewproduct.html', context)
    else:
            return redirect('adminlogin')
from django.shortcuts import get_object_or_404, redirect


def mark_variant_deleted(request):
    if request.method == 'POST':
        product_variant_color_id = request.POST.get('product_variant_color_id')
        product_variant_color = get_object_or_404(ProductVariantColor, id=product_variant_color_id)
        product_variant_color.variant_deleted = True
        product_variant_color.save()
        product =  product_variant_color.product_variant.product
        product_id = product.pk
        context = {
        'product': product,
         }
        return redirect(viewproduct,product_id )


def mark_variant_revoked(request):
    if request.method == 'POST':
        product_variant_color_id = request.POST.get('product_variant_color_id')
        product_variant_color = get_object_or_404(ProductVariantColor, id=product_variant_color_id)
        product_variant_color.variant_deleted = False
        product_variant_color.save()
        product =  product_variant_color.product_variant.product
        product_id = product.pk
        context = {
        'product': product,
         }
        return redirect(viewproduct,product_id )
    

def update_price_stock(request):
    if request.method == 'POST':
        product_variant_color_id = request.POST.get('product_variant_color_id')
        price = int(float(request.POST.get('price')))
        stock = request.POST.get('stock')
        product_variant_color = get_object_or_404(ProductVariantColor, id=product_variant_color_id)
        product_variant_color.price = price
        product_variant_color.stock = stock
        product_variant_color.save()
        product =  product_variant_color.product_variant.product
        context = {
        'product': product,
         }
        return render(request, 'adminpages/viewproduct.html', context)
    

# views.py

def add_new_variant(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                if request.method == 'POST':
                    variant_id = request.POST.get('variant')
                    product_id = request.POST.get('product_id')
                    color_variant = request.POST.get('color')
                    price = request.POST.get('price')
                    stock = request.POST.get('stock')
                    

                    try:
                        product = Product.objects.get(pk=product_id)
                        
                        variant = Variant.objects.get(pk=variant_id)
                        category = product.category
                        colorvariant = ColorVariant.objects.get(pk=color_variant)

                        # Try to get or create the ProductVariant instance
                        product_variant, created = ProductVariant.objects.get_or_create(
                            product=product,
                            variant=variant
                        )

                        # Check if the ProductVariantColor instance exists
                        product_variant_color_exists = ProductVariantColor.objects.filter(
                            product_variant=product_variant,
                            color_variant=colorvariant
                        ).exists()

                        if product_variant_color_exists:
                            # Show error message if the ProductVariantColor instance already exists
                            return JsonResponse({'success': False, 'message': 'Product variant  already exists.'})
                        else:
                            # Create the ProductVariantColor instance if it doesn't exist
                            ProductVariantColor.objects.create(
                                product_variant=product_variant,
                                color_variant=colorvariant,
                                price=price,
                                stock=stock,
                                category=category,
                                product=product
                            )

                        # Return success response with product ID
                            return JsonResponse({'success': True, 'product_id': product_id})

                    except IntegrityError:
                        # Handle any database-related errors or validation errors
                        # You can show an error message or return an error response
                        return JsonResponse({'success': False, 'message': 'An error occurred while adding the variant.'})
            else:
                return redirect('adminlogin') 

                



def cancel_orders_admin(request,order_id):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                order = get_object_or_404(Order, id=order_id)
                items = OrderItem.objects.filter(order=order)
                if order.status != 'PAID' and order.status != 'CANCELLED':
                        # Update the payment status to 'CANCELLED'
                        
                        order.status = 'CANCELLED'
                        order.save()

                        send_mail(
                            'Your order hasbeen cancelled',
                            f"Dear {order.user.username},\n\nYour order (ID: {order.id}) has been cancelled from our end. sorry for the inconviniance caused. contact our customer care for more details and assistance",
                            'your_email@example.com',  # Replace with your email address
                            [order.user.email],
                            fail_silently=False,
                        )
                        for order_item in items:
                            variant = order_item.product   
                            variant.stock += order_item.quantity
                            variant.save()
                            
                return redirect('ordertableadmin')
            else:
                return redirect('adminlogin')

# views.py
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from .models import ProductImage


def delete_image(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                if request.method == 'POST':
                    image_id = request.POST.get('image_id')
                    try:
                        # Find the image by ID and delete it
                        image = ProductImage.objects.get(pk=image_id)
                        image.delete()

                        return JsonResponse({'success': True})

                    except ProductImage.DoesNotExist:
                        # Image with the given ID does not exist
                        return JsonResponse({'success': False, 'message': 'Image not found'})

                # Handle other HTTP methods if needed
                # ...

                # Return a JsonResponse with appropriate error message if needed
                return JsonResponse({'success': False, 'message': 'Invalid request'})
            else:
                return redirect('adminlogin')





