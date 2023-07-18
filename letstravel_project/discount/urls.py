from django.urls import path
from . import views


urlpatterns = [
    path('addcoupon/',views.add_coupon, name='addcoupon'),
    path('coupon_list/',views.coupon_list, name='coupon_list'),
    path('change_coupon_status/<int:coupon_id>',views.change_coupon_status, name='change_coupon_status'),
    path('edit_coupon/<int:coupon_id>',views.edit_coupon, name='edit_coupon'),
    ]

