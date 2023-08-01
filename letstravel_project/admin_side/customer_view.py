
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from admin_side.models import Product
from admin_side.models import PhoneNumber
from django.contrib.auth.decorators import login_required,user_passes_test



def customer_list(request):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                query = request.GET.get('query')
                users = User.objects.all()
                
                if query:
                    users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
                
                paginator = Paginator(users, 10)  # Show 10 customers per page
                page_number = request.GET.get('page')
                page_users = paginator.get_page(page_number)
                return render(request, 'adminpages/customerlist.html', {'users': page_users, 'query': query})
            else:
                return redirect('adminlogin')

def editproduct(request,product_id):
    return render(request, 'adminpages/view_edit_products.html')

def edit_product(request,product_id):
    pass


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

        # Set the 'product_deleted' field to True
    product.product_deleted = True
    product.save()
        # Redirect to a success page or another view
    return redirect('productlist')

    
    

def revoke_product(request,product_id):

    product = get_object_or_404(Product, id=product_id)

        # Set the 'product_deleted' field to True
    product.product_deleted = False
    product.save()
        # Redirect to a success page or another view
    return redirect('productlist')




def viewcustomer(request, customer_id):
    if request.user.is_authenticated:
            if request.user.is_superuser:
                user = get_object_or_404(User, id=customer_id)
                try:
                    phone_number = PhoneNumber.objects.get(user=user)
                except PhoneNumber.DoesNotExist:
                    phone_number = None
                context = {
                    'user': user,
                    'phone_number': phone_number,
                }
                return render(request, 'adminpages/view_user.html', context)
            else:
                return redirect('adminlogin')


def bancustomer(request, customer_id):
    # Retrieve the customer instance
    customer = User.objects.get(id=customer_id)

    # Set the is_active field to False
    customer.is_active = False

    # Save the updated customer instance
    customer.save()
    return redirect('customerlist')


def unbancustomer(request, customer_id):
    # Retrieve the customer instance
    customer = User.objects.get(id=customer_id)

    # Set the is_active field to False
    customer.is_active = True

    # Save the updated customer instance
    customer.save()
    return redirect('customerlist')


def deletecustomer(request, customer_id):
    # Retrieve the customer instance
    customer = User.objects.get(id=customer_id)

    # Set the is_active field to False
    customer.is_staff= True

    # Save the updated customer instance
    customer.save()
    return redirect('customerlist')


def revokecustomer(request, customer_id):
    # Retrieve the customer instance
    customer = User.objects.get(id=customer_id)

    # Set the is_active field to False
    customer.is_staff= False

    # Save the updated customer instance
    customer.save()
    return redirect('customerlist')


