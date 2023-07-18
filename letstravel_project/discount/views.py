from django.shortcuts import render
# Create your views here.
from django.shortcuts import render, redirect
from .models import Coupon

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
