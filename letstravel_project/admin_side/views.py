from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control,never_cache

from admin_side.forms import ImageForm


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminlogin(request):

        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('dashboard')
            else:
            
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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlogin')
@never_cache
def dashboard(request):
    if request.user.is_superuser:
        users_data=User.objects.all()
        return render(request,'adminpages/dashboard.html',{'users':users_data})
    else:
        return redirect('home')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='adminlogin')
def admin_logout(request):
    logout(request)
    return redirect('adminlogin')








#add product
from django.shortcuts import render, redirect
from .models import Category, ColorVariant, Product, ProductImage, ProductVariant, Variant


# def add_product(request):
    

#     if request.method == 'POST':
        
#             category_id = request.POST.get('category')
#             variant_id=request.POST.get('variant')

#             name = request.POST.get('product_name')
#             tags = request.POST.get('product_tags')
#             quantity_left = request.POST.get('quantity_left')
#             description = request.POST.get('product_description')
            
#             color_variant_id = request.POST.get('colour')
#             price = request.POST.get('product_price')
#             code = request.POST.get ('product_code')

#             category = Category.objects.get(id=category_id)
#             variant = Variant.objects.get(id=variant_id)

#             product = Product(
#                 name=name,
#                 tags=tags,
#                 quantity_left=quantity_left,
#                 description=description,
#                 color_variant_id=color_variant_id,
#                 price=price,
#                 product_code=code,
#                 category=category, 
#                 variant=variant
#             )

#             product.save()

#             request.session['last_product_key'] = product.pk
#             print(request.session.get('last_product_key'))
#             return redirect('upload_images')
#     categories = Category.objects.all()
#     colors = ColorVariant.objects.all()

#     return render(request, 'adminpages/add_product.html', {
#         'categories': categories,
#         'colors': colors
#     })



from django.shortcuts import render, redirect
from .models import Product, Category, Variant, ColorVariant



def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        category_id = request.POST.get('category')
        
        variant_ids = request.POST.getlist('variants')
        product_description = request.POST.get('product_description')
        product_code = request.POST.get('product_code')
        
        # Validate and save the product details
        
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

        colors = ColorVariant.objects.all() 
        for variant_id in variant_ids:
            variant = get_object_or_404(Variant, id=variant_id)
            product_variant = ProductVariant(product=product, variant=variant)
            product_variant.save()

         # # Redirect to a success page or perform additional actions

        request.session['last_product_key'] = product.pk

        context = {
        'product_id': product.pk,
        'selected_variants': variant_ids,
        'product_variants': product.productvariant_set.all(),
        'colors': colors,
         
        }# Retrieve the associated product variants

        return render(request, 'adminpages/select_color.html', context)
        
    else:
        # Retrieve the categories and colors from the database
        categories = Category.objects.all()
        colors = ColorVariant.objects.all()
        
        context = {
            'categories': categories,
            'colors': colors,
        }

        return render(request, 'adminpages/add_product.html', context)
    









from django.shortcuts import render, redirect
from .models import ProductVariantColor

def save_product_variant_color(request):
    if request.method == 'POST':
        product_variant_id = request.POST.get('product_variant_id')
        color_variant_id = request.POST.get('color')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        
        # Create a new ProductVariantColor instance
        product_variant_color = ProductVariantColor(
            product_variant_id=product_variant_id,
            color_variant_id=color_variant_id,
            price=price,
            stock=stock
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
        colors = ColorVariant.objects.all()
        saved_color_ids = ProductVariantColor.objects.filter(product_variant__product=product_id).values_list('color_variant_id', flat=True)
        product_variant_colors = ProductVariantColor.objects.filter(product_variant__product=product_id)

        context = {
        'product_id': product_id,
        'product_variants': product_variants,
        'colors': colors,
        'saved_color_ids': saved_color_ids,
        'product_variant_colors':product_variant_colors
        }

        # Redirect to a success page or perform any desired action
        return render(request, 'adminpages/select_color.html', context)
    else:
        # Handle the case when the request method is not POST
        return redirect('error')  # Redirect to an error page or handle the case differently




from django.http import JsonResponse
def get_color_checkboxes(request):
    if request.method == "GET":
        color_variants = ColorVariant.objects.all()
        return render(request, "color_checkboxes.html", {"color_variants": color_variants})
    else:
        return JsonResponse({"message": "Invalid request method"})





#upload images


# def upload_images(request,product_variant_color_id):
    
        
#         uploaded_images= ProductImage.objects.filter(product_variant_color_id=product_variant_color_id)
#         product_id = request.session['last_product_key']
#         product = Product.objects.get(product_id)
#         product_name = product.name
#         product_variant_color = ProductVariantColor.objects.get(pk=product_variant_color_id)
        


        

#         form = ImageForm(request.POST or None, request.FILES or None)
#         if form.is_valid():
#             print("valid")
#             image = form.save(commit=False)
#             image.product_id = product_variant_color_id
#             image.save()
#             return JsonResponse({'message': 'Image uploaded successfully.'})

#         context = {'form': form , 'images':uploaded_images , 'name': product_name, 'product_id':product_id}
        
#         return render(request, 'adminpages/upload_images.html', context)
    

#          #return redirect('add_product')from django.shortcuts import get_object_or_404




from django.shortcuts import get_object_or_404

# def upload_images(request, product_variant_color_id):
#     # Retrieve the product variant color object using the provided ID
#     product_variant_color = get_object_or_404(ProductVariantColor, pk=product_variant_color_id)

#     # Retrieve the associated product variant object
#     product_variant = product_variant_color.product_variant

#     # Retrieve the product name using the product variant
#     product_name = product_variant.product.name

#     # Retrieve the variant name from the product variant
#     variant_name = product_variant.variant.name

#     # Retrieve the color name from the color variant
#     color_name = product_variant_color.color_variant.color

#     # Rest of your code
#     uploaded_images = ProductImage.objects.filter(product_variant_color_id=product_variant_color_id)
#     product_id = request.session['last_product_key']

#     form = ImageForm(request.POST or None, request.FILES or None)
#     if form.is_valid():
#         print("valid")
#         image = form.save(commit=False)
#         image.product_variant_color_id = product_variant_color_id
#         image.save()
#         return JsonResponse({'message': 'Image uploaded successfully.'})

#     context = {
#         'form': form,
#         'images': uploaded_images,
#         'name': product_name,
#         'product_id': product_id,
#         'variant_name': variant_name,
#         'color_name': color_name
#     }
        
#     return render(request, 'adminpages/upload_images.html', context)


def upload_images(request, product_variant_color_id):
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
        print("valid")
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



