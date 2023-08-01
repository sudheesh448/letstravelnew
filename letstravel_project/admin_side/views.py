import calendar
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import cache_control,never_cache
from admin_side.forms import ImageForm
from order.models import Order
from django.shortcuts import render, redirect
from .models import ProductVariantColor
from django.shortcuts import render, redirect
from .models import Category, ColorVariant, Product, ProductImage, ProductVariant, Variant
from django.shortcuts import render, redirect
from .models import Product, Category, Variant, ColorVariant
from django.db import IntegrityError
from datetime import datetime, timedelta
from django.db.models import Sum,Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime
from wkhtmltopdf.views import PDFTemplateView
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template import RequestContext
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.middleware.csrf import get_token
from django.middleware.clickjacking import XFrameOptionsMiddleware
from django.middleware.csrf import CsrfViewMiddleware


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminlogin(request):

        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('dashboard')
            else:
                logout(request)  # Logout the currently logged-in user
                return redirect('adminlogin')

        if request.method =='POST':
            user_name=request.POST['username']
            password1=request.POST['password']

            user=authenticate(username=user_name,password=password1)

            if user is not None:
                if user.is_superuser:

                    login(request,user)
                    return redirect('dashboard')
            else:
                messages.error(request,"invalid credentials")
                return redirect('adminlogin')
        return render(request,'adminpages/login.html') 




def dashboard(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                users_data=User.objects.all()
                total_orders = Order.get_total_orders()
                total_orders_week=Order.get_orders_count_week()
                total_orders_month=Order.get_orders_count_month()
                total_orders_day=Order.get_orders_count_day()
                total_revenue = Order.get_total_revenue()
                total_revenue_month=Order.get_total_revenue_month()
                total_revenue_week=Order.get_total_revenue_week()
                total_revenue_day=Order.get_total_revenue_day()

                if 'last_product_key' in request.session:
                    del request.session['last_product_key']
                    

                context={ 
                    'users_data':users_data,
                    'total_orders':total_orders,
                    'total_orders_week':total_orders_week,
                    'total_orders_month': total_orders_month,
                    'total_orders_day':total_orders_day,
                    'total_revenue':total_revenue,
                    'total_revenue_month':total_revenue_month,
                    'total_revenue_week':total_revenue_week,
                    'total_revenue_day':total_revenue_day
                }
                return render(request,'adminpages/dashboard.html',context)
            else:
                return redirect('adminlogin')
    


def admin_logout(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                logout(request)
                return redirect('adminlogin')



def add_product(request):

    if request.user.is_authenticated:
            if request.user.is_superuser:
                    if request.method == 'POST':
                        product_name = request.POST.get('product_name')
                        category_id = request.POST.get('category')
                        variant_ids = request.POST.getlist('variants')
                        product_description = request.POST.get('product_description')
                        product_code = request.POST.get('product_code')

                        try:
                            # Retrieve the selected category and color objects
                            category = Category.objects.get(id=category_id)

                            # Create the product instance
                            product = Product(
                                name=product_name,
                                category=category,
                                description=product_description,
                                product_code=product_code
                            )
                            product.save()

                            for variant_id in variant_ids:
                                variant = get_object_or_404(Variant, id=variant_id)
                                product_variant = ProductVariant(product=product, variant=variant)
                                product_variant.save()

                            request.session['last_product_key'] = product.pk

                            colors = ColorVariant.objects.all()
                            context = {
                                'product_id': product.pk,
                                'selected_variants': variant_ids,
                                'product_variants': product.productvariant_set.all(),
                                'colors': colors,
                            }

                            # Redirect to a success page or perform additional actions
                            return render(request, 'adminpages/select_color.html', context)

                        except IntegrityError as e:
                            messages.error(request, "A product with the same name or product code already exists.")
                            categories = Category.objects.all()
                            colors = ColorVariant.objects.all()

                            context = {
                                'categories': categories,
                                'colors': colors,
                            }

                            return render(request, 'adminpages/add_product.html', context)

                    else:
                        categories = Category.objects.all()
                        colors = ColorVariant.objects.all()
                        
                        context = {
                            'categories': categories,
                            'colors': colors,
                        }

                        return render(request, 'adminpages/add_product.html', context)
            else:
                return redirect('adminlogin')
        
    






def save_product_variant_color(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                if request.method == 'POST':
                    product_variant_id = request.POST.get('product_variant_id')
                    color_variant_id = request.POST.get('color')
                    price = request.POST.get('price')
                    stock = request.POST.get('stock')
                    product_id = request.session['last_product_key']
                    product_variants = ProductVariant.objects.filter(product=product_id)
                    product = get_object_or_404(Product, id=product_id)
                    category_id = product.category.id  # Get the category ID
                    category = get_object_or_404(Category, id=category_id)

                    product_variant = get_object_or_404(ProductVariant, id=product_variant_id)
                    color_variant = get_object_or_404(ColorVariant, id=color_variant_id)
                    

                    try:
                        product_variant_color = ProductVariantColor.objects.get(
                            product_variant=product_variant,
                            color_variant=color_variant
                        )
                    except ProductVariantColor.DoesNotExist:# Create a new ProductVariantColor instance
                        product_variant_color = ProductVariantColor(
                            product_variant=product_variant,
                            color_variant=color_variant,
                            price=price,
                            stock=stock,
                            category=category,
                            product=product
                        )
                        product_variant_color.save()



                    def get_product_id(request):
                        product_variant_id = request.POST.get('product_variant_id')
                        product_variant = ProductVariant.objects.get(id=product_variant_id)
                        return product_variant.product_id

                    def get_associated_variants(request):
                        product_variant_id = request.POST.get('product_variant_id')
                        product_variant = ProductVariant.objects.get(id=product_variant_id)
                        return product_variant.product.variant_set.all()
                    
                    product_id = request.session['last_product_key']
                    product_variants = ProductVariant.objects.filter(product=product_id)
                    product = get_object_or_404(Product, id=product_id)
                    category_id = product.category.id  # Get the category ID
                    category = get_object_or_404(Category, id=category_id)
                    colors = ColorVariant.objects.all()
                    saved_color_ids = ProductVariantColor.objects.filter(product_variant__product=product_id).values_list('color_variant_id', flat=True)
                    product_variant_colors = ProductVariantColor.objects.filter(product_variant__product=product_id)

                    context = {
                    'product_id': product_id,
                    'product_variants': product_variants,
                    'colors': colors,
                    'saved_color_ids': saved_color_ids,
                    'product_variant_colors':product_variant_colors,
                    'category_id': category_id,  # Pass the category ID to the context
                    'category': category,
                    }
                    # Redirect to a success page or perform any desired action
                    return render(request, 'adminpages/select_color.html', context)
                else:
                    context = {
                    'product_id': product_id,
                    'product_variants': product_variants,
                    'colors': colors,
                    'saved_color_ids': saved_color_ids,
                    'product_variant_colors':product_variant_colors,
                    'category_id': category_id,  # Pass the category ID to the context
                    'category': category,
                    }
                    # Handle the case when the request method is not POST
                    return render(request, 'adminpages/select_color.html', context)
            else:
                return redirect('adminlogin')            
    
from django.http import JsonResponse
def get_color_checkboxes(request):
    if request.method == "GET":
        color_variants = ColorVariant.objects.all()
        return render(request, "color_checkboxes.html", {"color_variants": color_variants})
    else:
        return JsonResponse({"message": "Invalid request method"})



def upload_images(request, product_variant_color_id):
    if request.user.is_authenticated:
            if request.user.is_superuser:
    # Retrieve the product variant color object using the provided ID
                product_variant_color = get_object_or_404(ProductVariantColor, pk=product_variant_color_id)

                # Retrieve the associated product variant object
                product_variant = product_variant_color.product_variant

                # Retrieve the product name using the product variant
                product_name = product_variant.product.name

                # Retrieve the variant name from the product variant
                variant_name = product_variant.variant.name

                # Retrieve the color name from the color variant
                color_name = product_variant_color.color_variant.color

                # Rest of your code
                uploaded_images = ProductImage.objects.filter(product_variant_color_id=product_variant_color_id)
                product_id = request.session['last_product_key']

                form = ImageForm(request.POST or None, request.FILES or None)
                if form.is_valid():
                    
                    image = form.save(commit=False)
                    image.product_variant_color_id = product_variant_color_id
                    image.save()
                    return JsonResponse({'message': 'Image uploaded successfully.'})

                context = {
                    'form': form,
                    'images': uploaded_images,
                    'product_name': product_name,
                    'product_id': product_id,
                    'variant_name': variant_name,
                    'color_name': color_name
                }
                    
                return render(request, 'adminpages/upload_images.html', context)
            else:
                return redirect('adminlogin')   




def revenue_chart_data(request):
    # Calculate the start and end dates for the past 7 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)

    # Query the Order model to get the revenue for each day
    revenue_data = Order.objects.filter(order_date__date__range=(start_date, end_date)).values('order_date__date').annotate(revenue=Sum('total_price')).order_by('order_date__date')

    # Prepare the data for the chart
    labels = []
    revenue = []
    for data in revenue_data:
        labels.append(data['order_date__date'].strftime('%Y-%m-%d'))
        revenue.append(data['revenue'])

    # Return the data as a JSON response
    data = {
        'labels': labels,
        'datasets': [{
            'label': 'Revenue',
            'data': revenue,
            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            'borderColor': 'rgba(255, 99, 132, 1)',
            'borderWidth': 1,
            'fill': False
        }]
    }
    return JsonResponse(data)

def payment_chart_data(request):
    # Query the Order model to count the number of orders for each payment method
    payment_data = Order.objects.values('payment_method').annotate(count=Count('payment_method'))

    # Prepare the data for the chart
    labels = []
    counts = []
    for data in payment_data:
        labels.append(data['payment_method'])
        counts.append(data['count'])

    # Return the data as a JSON response
    data = {
        'labels': labels,
        'datasets': [{
            'data': counts,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.5)',
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(75, 192, 192, 0.5)',
                'rgba(153, 102, 255, 0.5)',
                'rgba(255, 159, 64, 0.5)'
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
        }],
    }
    return JsonResponse(data)


def order_status_chart_data(request):
    order_status_data = Order.objects.values('status').annotate(count=Count('status')).order_by()
    labels = []
    counts = []
    for data in order_status_data:
        labels.append(data['status'])
        counts.append(data['count'])
    data = {
        'labels': labels,
        'datasets': [{
            'data': counts,
            'backgroundColor': [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#79FBE7',
                
            ],
            'hoverBackgroundColor': [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#79FBE7',
                
            ]
        }]
    }
    return JsonResponse(data)


def revenue_chart_line(request):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30*6)  # Past 6 months

    revenue_data = Order.objects.filter(order_date__date__range=(start_date, end_date)).values('order_date__month').annotate(revenue=Sum('total_price')).order_by('order_date__month')

    labels = []
    revenue = []
    for data in revenue_data:
        month_number = data['order_date__month']
        month_name = calendar.month_name[month_number]
        labels.append(month_name)
        revenue.append(data['revenue'])

    data = {
        'labels': labels,
        'datasets': [{
            'label': 'Revenue',
            'data': revenue,
            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            'borderColor': 'rgba(255, 99, 132, 1)',
            'borderWidth': 1,
            'fill': False
        }]
    }
    return JsonResponse(data)




def sales_report_view(request):
    # Get the required data for the sales report
    total_orders = Order.get_total_orders()
    total_revenue = Order.get_total_revenue()
    total_revenue_month = Order.get_total_revenue_month()
    total_revenue_week = Order.get_total_revenue_week()
    total_revenue_day = Order.get_total_revenue_day()
    
    # Get the total number of orders for the month, week, and day
    total_orders_month = Order.get_orders_count_month()
    total_orders_week = Order.get_orders_count_week()
    total_orders_day = Order.get_orders_count_day()

    # Get the report generated date and time
    report_generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Pass the data to the template context
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_revenue_month': total_revenue_month,
        'total_revenue_week': total_revenue_week,
        'total_revenue_day': total_revenue_day,
        'total_orders_month': total_orders_month,
        'total_orders_week': total_orders_week,
        'total_orders_day': total_orders_day,
        'report_generated_date': report_generated_date,
    }

    # Render the sales report template with the data
    return render(request, 'adminpages/salesreport.html', context)






