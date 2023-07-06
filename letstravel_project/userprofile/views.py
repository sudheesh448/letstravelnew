from django.http import HttpResponse
from django.shortcuts import redirect, render

from userprofile.models import UserAddress


def address(request):
    address = UserAddress.objects.filter(user=request.user)
    context = {
        'address':address
    }  
    return render(request, 'userprofile/address.html',context)


def add_address(request):
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