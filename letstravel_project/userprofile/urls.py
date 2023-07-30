from django.urls import path
from . import views


urlpatterns = [
    path('address/',views.address, name='address'),
    path('add_address/',views.add_address,name='add_address'),
    path('edit_address/<int:address_id>',views.edit_address,name='edit_address'),
    path('user_address/',views.user_address,name='user_address'),
    path('profile_view/',views.profile_view,name='profile_view'),
    path('delete_address/',views.delete_address,name='delete_address'), 
    path('edit_address_profile/<int:address_id>',views.edit_address_profile,name='edit_address_profile'), 
]
