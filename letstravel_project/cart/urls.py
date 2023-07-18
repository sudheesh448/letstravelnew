from django.urls import path
from . import views


urlpatterns = [
    path('addtocart/',views.addtocart, name='addtocart'),
    path('shoppingcart/',views.shoppingcart, name='shoppingcart'),
    path('remove_from_cart/',views.remove_from_cart, name='remove_from_cart'),
    path('decrement_quantity/',views.decrement_quantity, name='decrement_quantity'),
    path('increment_quantity/',views.increment_quantity, name='increment_quantity'),
    path('apply_coupon/',views.apply_coupon, name='apply_coupon'),
    
]
