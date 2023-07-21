from django.urls import path
from . import views


urlpatterns = [
    path('addcoupon/',views.add_coupon, name='addcoupon'),
    path('coupon_list/',views.coupon_list, name='coupon_list'),
    path('change_coupon_status/<int:coupon_id>',views.change_coupon_status, name='change_coupon_status'),
    path('edit_coupon/<int:coupon_id>',views.edit_coupon, name='edit_coupon'),
    path('create_category_offer',views.create_category_offer, name='create_category_offer'),
    path('view_category_offers',views.view_category_offers, name='view_category_offers'),
    path('activate_offer/<int:offer_id>',views.activate_offer, name='activate_offer'),
    path('inactivate_offer/<int:offer_id>',views.inactivate_offer, name='inactivate_offer'),
    
    ]


