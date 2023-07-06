from django.shortcuts import render
from django.shortcuts import redirect, render
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




def viewproduct(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product
    }
    return render(request, 'adminpages/viewproduct.html', context)



# def viewproduct(request):
#     try:
#         print(request.session.get('last_product_key'))

#         productid={'id':request.session['last_product_key']}

#         #del request.session['last_product_key']
        
#         print(request.session.get('last_product_key'))


#         return render(request, 'adminpages/viewproduct.html',productid)
#     except:
#          return render(request, 'adminpages/viewproduct.html')
    


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


from .models import Category, Variant

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








# def addvariants(request):
#     category_id=request.session['last_category_key']
    
#     category = Category.objects.get(id=category_id)
#     name=category.name
    
#     if request.method == 'POST':
#         name = request.POST['name']
#         variant = Variant(name=name, category=category)
#         variant.save()
#         return redirect('dashboard', category_id=category_id)
    
#     return render(request, 'adminpages/addvariants.html', {'category': name})


# def categoryview(request):

#     categorylist = Category.objects.prefetch_related('variants').all()

#     return render(request, 'adminpages/categorylist.html',{'categorylist':categorylist})
    


from django.core.paginator import Paginator

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Category

def category_view(request):
    search_query = request.GET.get('search')
    
    category_list = Category.objects.prefetch_related('variants').all()
    
    if search_query:
        category_list = category_list.filter(Q(name__icontains=search_query))
    
    paginator = Paginator(category_list, 10)  # Show 10 categories per page
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)
    
    return render(request, 'adminpages/categorylist.html', {'categories': categories, 'search_query': search_query})







from django.shortcuts import get_object_or_404, render, redirect

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Category, Variant

# def category_update(request, category_id):
#     category = get_object_or_404(Category, pk=category_id)
    
#     if request.method == 'POST':
#         # Update Category fields
#         category.name = request.POST.get('name')
#         category.description = request.POST.get('description')
#         category.save()
        
#         # Delete Variants if necessary
#         variant_ids = request.POST.getlist('delete_variant')
#         Variant.objects.filter(id__in=variant_ids, category=category).delete()
        
#         return redirect('category_update', category_id=category_id)
    
#     variants = category.variants.all()
    
#     return render(request, 'adminpages/category_update.html', {'category': category, 'variants': variants})



# import json

# def add_variant(request):
#     if request.method == 'POST' and request.is_ajax():
#         category_id = request.POST.get('category_id')
#         variant_name = request.POST.get('variant_name')
        
#         # Perform validation and save the variant
        
#         # Example response
#         response_data = {
#             'success': True,
#             'message': 'Variant added successfully',
#         }
#         return JsonResponse(response_data)
    
#     # If the request is not a POST or not an AJAX request, return an error response
#     response_data = {
#         'success': False,
#         'message': 'Invalid request',
#     }
#     return JsonResponse(response_data, status=400)



from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, Variant

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



from django.shortcuts import render
from .models import Category, Variant, Product, ProductImage
from django.core.paginator import Paginator




# def productlist(request):
#     query = request.GET.get('query')
    
#     if query:
#         products = Product.objects.select_related('category').prefetch_related('variants', 'color_variant', 'images').filter(name__icontains=query)
#     else:
#         products = Product.objects.select_related('category').prefetch_related('variants', 'color_variant', 'images').all()
    
#     paginator = Paginator(products, 10)  # Show 10 products per page
#     page_number = request.GET.get('page')
#     page_products = paginator.get_page(page_number)
    
#     return render(request, 'adminpages/productlist.html', {'products': page_products, 'query': query})






from django.shortcuts import render
from .models import Product, ProductVariant, ProductVariantColor, ProductImage


from django.core.paginator import Paginator

from django.db.models import Q

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
    order_list = Order.objects.all()

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





