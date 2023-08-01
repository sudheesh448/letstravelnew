import datetime
from django.shortcuts import render
# Create your views here.
from django.shortcuts import render, redirect
from .models import Coupon
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CategoryOffer
from django.shortcuts import render
from .models import CategoryOffer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CategoryOffer

def add_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        discount = request.POST.get('discount')
        expiry_date = request.POST.get('expiry_date')
        available = request.POST.get('available')
        is_percentage = bool(request.POST.get('is_percentage'))
        min_order_total = request.POST.get('min_order_total')
        max_discount_amount = request.POST.get('max_discount_amount')
        
        coupon = Coupon(
            code=code,
            discount=discount,
            expiry_date=expiry_date,
            available=available,
            is_percentage=is_percentage,
            min_order_total=min_order_total,
            max_discount_amount=max_discount_amount
        )
        coupon.save()
        
        return redirect('coupon_list')
    
    return render(request, 'coupon/add_coupon.html')

from django.core.paginator import Paginator

def coupon_list(request):
    coupons = Coupon.objects.order_by('-id')
    paginator = Paginator(coupons, 10)  # Show 10 coupons per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'coupon/coupon_list.html', context)



from django.http import HttpResponseRedirect

def change_coupon_status(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    coupon.is_active = not coupon.is_active
    coupon.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



from django.shortcuts import render, get_object_or_404, redirect
from .models import Coupon

def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)

    if request.method == 'POST':
        # Process the form data and update the coupon
        coupon.code = request.POST['code']
        coupon.discount = request.POST['discount']
        coupon.expiry_date = request.POST['expiry_date']
        coupon.available = request.POST['available']
        coupon.is_percentage = bool(request.POST.get('is_percentage'))
        coupon.min_order_total = request.POST['min_order_total']
        coupon.max_discount_amount = request.POST['max_discount_amount']
        coupon.save()
        return redirect('coupon_list')

    formatted_expiry_date = coupon.expiry_date.strftime('%Y-%m-%d')

    context = {'coupon': coupon, 'formatted_expiry_date': formatted_expiry_date}
    return render(request, 'coupon/edit_coupon.html', context)


# views.py
from django.shortcuts import render, redirect
from .models import CategoryOffer
from .models import Category
from django.http import HttpResponse

def create_category_offer(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        offer_description = request.POST.get('offer_description')
        discount_percentage = request.POST.get('discount_percentage')
        expiry_date = request.POST.get('expiry')



        if category_id and discount_percentage and expiry_date:
            category = Category.objects.get(pk=category_id)
            category_offer = CategoryOffer.objects.create(
                category=category,
                offer_description=offer_description,
                discount_percentage=float(discount_percentage),
                 expiry_date=expiry_date,
            )
            # You can add more logic here if needed, such as setting success messages or redirecting to a success page.
            messages.success(request, f"Category Offer created: {category_offer}")
            return redirect('view_category_offers')
        else:
            # Handle form validation errors here, such as displaying error messages or redirecting back to the form page.
            messages.error(request, "Please fill in all required fields.")
            return redirect('create_category_offer')
    else:
        # You can add any initial data or context here if needed.
        context = {
            'categories': Category.objects.all(),
        }
        return render(request, 'coupon/categoryoffer.html', context)





def activate_offer(request, offer_id):
    try:
        offer = CategoryOffer.objects.get(pk=offer_id)

        # Check if any other offer for the same category is active
        if CategoryOffer.objects.filter(category=offer.category, is_active=True).exclude(pk=offer_id).exists():
            active_offer = CategoryOffer.objects.filter(category=offer.category, is_active=True).first()
            messages.error(request, f"An offer with ID {active_offer.pk} is already active for this category.")
        else:
            # Activate the selected offer
            offer.is_active = True
            offer.save()
            messages.success(request, f"Offer with ID {offer.pk} has been activated successfully.")
        
        return redirect('view_category_offers')  # Replace 'offer_list' with the name of your view that displays the list of offers
    except CategoryOffer.DoesNotExist:
        messages.error(request, "Invalid offer ID.")
        return redirect('view_category_offers')  # Replace 'offer_list' with the name of your view that displays the list of offers
    



def inactivate_offer(request, offer_id):
    try:
        offer = get_object_or_404(CategoryOffer, pk=offer_id)

        # Inactivate the offer
        offer.is_active = False
        offer.save()

        messages.success(request, f"Offer with ID {offer.pk} has been inactivated successfully.")
    except CategoryOffer.DoesNotExist:
        messages.error(request, "Invalid offer ID.")

    return redirect('view_category_offers')  # Replace 'offer_list' with the name of your view that displays the list of offers




def view_category_offers(request):
    # Fetch all CategoryOffer instances, sorted by the latest first (based on expiry_date)
    category_offers = CategoryOffer.objects.order_by('-expiry_date')

    return render(request, 'coupon/categoryofferview.html', {'category_offers': category_offers})