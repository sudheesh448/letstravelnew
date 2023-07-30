from django.urls import path
from . import views


urlpatterns = [
     path('add_to_wishlist/',views.add_to_wishlist, name='add_to_wishlist'),
     path('remove_from_wishlist/',views.remove_from_wishlist, name='remove_from_wishlist'),
     path('view_wishlist/',views.view_wishlist, name='view_wishlist'),
     path('add_to_wishlist_product_detail/',views.add_to_wishlist_product_detail, name='add_to_wishlist_product_detail'),
    
    #  path('add_to_wishlist/',views.add_to_wishlist, name='add_to_wishlist'),
 ]
