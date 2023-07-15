from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control,never_cache
from admin_side.forms import ImageForm
from order.models import OrderItem
from order.models import Order
from .models import Category
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



def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        # Create a new category object
        category = Category.objects.create(name=name, description=description)
        # Redirect to a success page or another view
        request.session['last_category_key'] = category.pk
        print( request.session['last_category_key'])
        return redirect('addvariants')  
    return render(request, 'adminpages/addcategory.html')


def addvariants(request):
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


def category_view(request):
    search_query = request.GET.get('search')
    category_list = Category.objects.prefetch_related('variants').all()
    if search_query:
        category_list = category_list.filter(Q(name__icontains=search_query))
    paginator = Paginator(category_list, 10)  # Show 10 categories per page
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number) 
    return render(request, 'adminpages/categorylist.html', {'categories': categories, 'search_query': search_query})



def category_update(request, category_id):
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





def productlist(request):
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

def ordertableadmin(request):
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

def order_viewadmin(request,order_id):
    orderss = Order.objects.get(id=order_id)
    view_order = OrderItem.objects.filter(order=orderss)
    context ={
        'view_order':view_order
    }
    return render(request,"adminpages/order_viewadmin.html",context)


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
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description') 
        product.name = name
        product.description = description
        product.save()   
    category = product.category
    variants = Variant.objects.filter(category_id=category.pk)
    context = {
        'product': product,
        'variants':variants,
    }
    return render(request, 'adminpages/viewproduct.html', context)
from django.shortcuts import get_object_or_404, redirect


def mark_variant_deleted(request):
    if request.method == 'POST':
        product_variant_color_id = request.POST.get('product_variant_color_id')
        product_variant_color = get_object_or_404(ProductVariantColor, id=product_variant_color_id)
        product_variant_color.variant_deleted = True
        product_variant_color.save()
        product =  product_variant_color.product_variant.product
        context = {
        'product': product,
         }
        return render(request, 'adminpages/viewproduct.html', context)

    
def mark_variant_revoked(request):
    if request.method == 'POST':
        product_variant_color_id = request.POST.get('product_variant_color_id')
        product_variant_color = get_object_or_404(ProductVariantColor, id=product_variant_color_id)
        product_variant_color.variant_deleted = False
        product_variant_color.save()
        product =  product_variant_color.product_variant.product
        context = {
        'product': product,
         }
        return render(request, 'adminpages/viewproduct.html', context)
    

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
    

def add_new_variant(request):
    variant  = request.POST.get('variant')    
    product_id = request.POST.get('product_id')
    product_variant = ProductVariant.objects.create(product=product_id, variant=variant)
    pass

def cancel_orders_admin(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'PAID' and order.status != 'CANCELLED':
            # Update the payment status to 'CANCELLED'
            print(order.user.email) 
            order.status = 'CANCELLED'
            order.save()

            send_mail(
                'Your order hasbeen cancelled',
                f"Dear {order.user.username},\n\nYour order (ID: {order.id}) has been cancelled from our end. sorry for the inconviniance caused. contact our customer care for more details and assistance",
                'your_email@example.com',  # Replace with your email address
                [order.user.email],
                fail_silently=False,
            )
    return redirect('ordertableadmin')




