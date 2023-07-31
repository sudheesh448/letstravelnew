import random
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from admin_side.models import Product

# def home(request):
#     products = Product.objects.all()
#     return render(request, 'products/index.html', {'products': products})
# # Create your views here.

from django.core.paginator import Paginator

from admin_side.models import ProductImage
from admin_side.models import ColorVariant
from wishlist.models import Wishlist, WishlistItem


def home(request, category_id=None):
    # Assuming 'Product' is your model and you want to fetch all products
    query = request.GET.get('query')
    if query:
        # If a search query is provided, call the 'shop' view with the query
        return shop(request, query)
    
    products = Product.objects.select_related('category').prefetch_related(
        'variants__productvariant_set__productvariantcolor_set__productimage_set'
    )
    
    # Number of items per page
    items_per_page = 10
    # Create a Paginator object
    paginator = Paginator(products, items_per_page)
    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')
    # Get the Page object for the requested page number
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        user = request.user
        
        # Fetch the user's wishlist or create one if it doesn't exist
        wishlist, created = Wishlist.objects.get_or_create(user=user)

        # Fetch the wishlist items for the user
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
        wishlist_items_product_variant_color_ids = list(wishlist_items.values_list('product_variant_color__id', flat=True))
        context = {
        'products': page,
         'wishlist_items_product_variant_color_ids': wishlist_items_product_variant_color_ids,
         }
    else:
        context = {
        'products': page,
         }
    return render(request, 'products/index.html', context)



from django.shortcuts import render, get_object_or_404
from admin_side.models import Product, ProductVariant, ProductVariantColor


def productdetails(request, slug):


    try:
        product_variant_color = ProductVariantColor.objects.get(slug=slug)
    except ProductVariantColor.DoesNotExist:
        # Handle the case when the ProductVariantColor with the given slug does not exist
        # For example, you can return a custom 404 page
        return render(request, '404/404.html', status=404)
    product = product_variant_color.product_variant.product
    # colors = ColorVariant.objects.filter(productvariantcolor__product_variant = product_variant_color.product_variant)
    # variants = product.variants.all()
    category = product.category
    
    related = ProductVariantColor.objects.all()
    related = related.filter(category=category)
    related =random.sample(list(related), min(6, len(related)))
    

    context = {
        'productvariantcolor': product_variant_color,
        'product': product,
        # 'color_variant': colors,
        # 'variants': variants,
        'selectedVariantId': product_variant_color.product_variant.id,
        'productVariantColorId': product_variant_color.id,
        'related':related,
    }

    return render(request, 'products/product-detail.html', context)

    from django.http import JsonResponse

def getcolorids(request):
    variant_id = request.GET.get('variant_id')
    product_variant_colors = ProductVariantColor.objects.filter(product_variant_id=variant_id).prefetch_related('productimage_set')

    # Filter out product_variant_colors without images
    color_ids = [pvc.id for pvc in product_variant_colors if pvc.productimage_set.exists()]

    return JsonResponse({'color_ids': color_ids})

def getcolorname(request):
    color_id = request.GET.get('color_id')

    try:
        product_variant_color = ProductVariantColor.objects.get(pk=color_id)
        
        color_name = product_variant_color.color_variant.color
        slug = product_variant_color.slug
        productvariantcolor_id = product_variant_color.pk


        response = {
            'color_name': color_name,
            'slug': slug,
            'productvariantcolor_id': productvariantcolor_id
        }
        return JsonResponse(response)
    except ProductVariantColor.DoesNotExist:
        return JsonResponse({'error': 'Product variant color not found'}, status=404)

from django.core.paginator import Paginator
from django.shortcuts import render


def shop(request, query=None,category_id=None):
    if 'category_id' in request.session:
        # If category_id is None and it exists in the session, delete the 'category_id' session variable
        del request.session['category_id']
    if 'search_query' in request.session:
        del request.session['search_query']
    # If the 'query' parameter is provided, use it directly
    if query is not None:
        search_query = query
    else:
        # If the 'query' parameter is not provided, get it from the request's GET parameters
        search_query = request.GET.get('query', '')
    # Assuming 'Product' is your model and you want to fetch all products
    products = Product.objects.select_related('category').prefetch_related(
        'variants__productvariant_set__productvariantcolor_set__productimage_set'
    )
    # Filter products based on the search query if it's not empty
    if search_query:
        request.session['search_query'] = search_query
        products = products.filter(name__icontains=search_query)
    if category_id is not None:
        # Category ID is provided
        request.session['category_id'] = category_id
        # Filter products based on the category ID
        products = products.filter(category_id=category_id)

    
    # Number of items per page
    items_per_page = 10
    # Create a Paginator object
    paginator = Paginator(products, items_per_page)
    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')
    # Get the Page object for the requested page number
    page = paginator.get_page(page_number)

    user = request.user
    
    if user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
        wishlist_items_product_variant_color_ids = list(wishlist_items.values_list('product_variant_color__id', flat=True))
        context = {
        'products': page,
        'search_query': search_query,  # Pass the search query to the template
        'category_id': category_id,
        'wishlist_items_product_variant_color_ids': wishlist_items_product_variant_color_ids
    }
    else:
         context = {
        'products': page,
        'search_query': search_query,  # Pass the search query to the template
        'category_id': category_id,
    }

        # If the user is anonymous, create a dummy wishlist with None as the user
        
    return render(request, 'products/shop.html', context)

from django.db.models import Q

def shop_filter(request):
    category_id = request.session.get('category_id')
    search_query = request.session.get('search_query')
    price_filters = request.GET.getlist('price')
    all_colors = ColorVariant.objects.all()
    sort_new = request.GET.getlist('sort_new')
    sort_price = request.GET.get('sort_price')
    out_of_stock = request.GET.get('out_of_stock')
    

    # Assuming 'Product' is your model and you want to fetch all products
    products = ProductVariantColor.objects.all()
    color_filters = request.GET.getlist('color')

    if search_query:
        # Assuming 'product' is the foreign key field linking to the 'Product' model
        products = products.filter(product__name__icontains=search_query)

    if category_id is not None:
        # Assuming 'category' is the foreign key field linking to the 'Category' model
        products = products.filter(category=category_id)

    if price_filters and 'all' not in price_filters:
        # Extract the price range values and convert them to integers
        price_ranges = [tuple(map(int, price_filter.split('-'))) for price_filter in price_filters]
        price_filter_query = Q()  # Initialize an empty Q object for filtering

        for min_price, max_price in price_ranges:
            # Add price range conditions to the Q object using OR (|) operator
            price_filter_query |= Q(price__range=(min_price, max_price))

        # Apply the price filter to the products
        products = products.filter(price_filter_query)

    if color_filters and 'all' not in color_filters:
        # Filter products based on the selected colors
        products = products.filter(color_variant__color__in=color_filters)
    
    products = products.exclude(productimage__isnull=True)

    if out_of_stock:
        pass
    else:
        products = products.filter(stock__gt=0)

    # Sorting the products based on the selected option
    if  sort_new:
        # Filter products based on the selected "Sort New" options (checkboxes)
        for sort_option in sort_new:
            if sort_option == 'popularity':
                products = products.order_by('-popularity')
            elif sort_option == 'newness':
                products = products.order_by('-created_at')

    if sort_price:
        # Filter products based on the selected "Sort Price" option (radio button)
        if sort_price == 'low_to_high':
            products = products.order_by('price')
        elif sort_price == 'high_to_low':
            products = products.order_by('-price')

    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    user = request.user

    if user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
        wishlist_items_product_variant_color_ids = list(wishlist_items.values_list('product_variant_color__id', flat=True))

        context = {
        'products': products,
        'price_filters': price_filters,
        'color_filters': color_filters,
        'all_colors': all_colors,
        'sort_new': sort_new,
        'sort_price': sort_price,
        'out_of_stock': out_of_stock,
        'wishlist_items_product_variant_color_ids': wishlist_items_product_variant_color_ids
         }
    else:
        context = {
        'products': products,
        'price_filters': price_filters,
        'color_filters': color_filters,
        'all_colors': all_colors,
        'sort_new': sort_new,
        'sort_price': sort_price,
        'out_of_stock': out_of_stock,}

    
    return render(request, 'products/shop _filter.html', context)


    


