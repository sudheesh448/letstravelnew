from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from cart.models import Cart
from django.contrib import messages
from admin_side.models import PhoneNumber
from userprofile.models import UserAddress


def address(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    address = UserAddress.objects.filter(user=request.user)
    context = {
        'address':address
    }  
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.total_items == 0:
        messages.error(request, 'Your cart is empty.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'userprofile/address.html',context)


def add_address(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    if request.method == 'POST':
        # Get form data from the request
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        address_line_1 = request.POST.get('address1')
        address_line_2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('pincode')
        country = request.POST.get('country')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone')
        # Create a new UserAddress object and save it to the database
        user_address = UserAddress(
            user=request.user,  # Assuming the request has a logged-in user
            first_name=first_name,
            last_name=last_name,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            email=email,
            phone_number=phone_number
        )
        user_address.save()
        return redirect('address')
    return render(request,'userprofile/add_address.html')


def edit_address(request,address_id):
     if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
     try:
        user_address = UserAddress.objects.get(id=address_id, user=request.user)
     except UserAddress.DoesNotExist:
        return HttpResponse('Address not found.')
     if request.method == 'POST':
        # Get form data from the request
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        address_line_1 = request.POST.get('address1')
        address_line_2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('pincode')
        country = request.POST.get('country')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone')
        # Update the user address fields
        user_address.first_name = first_name
        user_address.last_name = last_name
        user_address.address_line_1 = address_line_1
        user_address.address_line_2 = address_line_2
        user_address.city = city
        user_address.state = state
        user_address.postal_code = postal_code
        user_address.country = country
        user_address.email = email
        user_address.phone_number = phone_number
        # Save the updated user address
        user_address.save()
        return redirect('address')
     context = {
         'user_address':user_address
     }
     return render(request,'userprofile/edit_address.html',context)


def profile_view(request):
     if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
     if request.method == 'POST':
        # Get the form data from the request
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        # Update the user object with the new information
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save() 
        return redirect('profile_view')  # Redirect to the profile view or any other desired page after updating
     address = UserAddress.objects.filter(user = request.user)
     try:
        phone_number = PhoneNumber.objects.get(user=request.user)
        referral_code = phone_number.referral_code
        context = {
        'address':address,
        'referral_code': referral_code,
     }
     except PhoneNumber.DoesNotExist:
        context = {
        'address':address,
        
     }
     
     return render(request,'profile/profile.html',context)


def user_address(request):
    if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
    user_add = request.user
    address = UserAddress.objects.filter(user = user_add)
    context = {
        'address':address,
        
    }
    return render(request,'userprofile/address.html',context) 
def delete_address(request):
     if request.method == 'POST':
        user_add_id = request.POST.get('user_add_id')  
        useraddress = UserAddress.objects.get(id=user_add_id)
        useraddress.delete()
        return redirect('profile_view')
     

def edit_address_profile(request,address_id):
     if not request.user.is_authenticated:
        messages.error(request,"Please sign in to continue")
        return redirect( 'signin')
     try:
        user_address = UserAddress.objects.get(id=address_id, user=request.user)
     except UserAddress.DoesNotExist:
        return HttpResponse('Address not found.')
     if request.method == 'POST':
        # Get form data from the request
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        address_line_1 = request.POST.get('address1')
        address_line_2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('pincode')
        country = request.POST.get('country')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone')
        # Update the user address fields
        user_address.first_name = first_name
        user_address.last_name = last_name
        user_address.address_line_1 = address_line_1
        user_address.address_line_2 = address_line_2
        user_address.city = city
        user_address.state = state
        user_address.postal_code = postal_code
        user_address.country = country
        user_address.email = email
        user_address.phone_number = phone_number
        # Save the updated user address
        user_address.save()
        return redirect('profile_view')
     context = {
         'user_address':user_address
     }
     return render(request,'profile/edit_address.html',context)
     
