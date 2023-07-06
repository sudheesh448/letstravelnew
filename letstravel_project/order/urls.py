from django.urls import path
from . import views


urlpatterns = [
    path('checkout/<int:address_id>',views.checkout,name='checkout'),
    path('place_order/<int:add_user_id>',views.place_order,name='place_order'),
    path('ordertable',views.ordertable,name="ordertable"),
    path('order_view/<int:order_id>',views.order_view,name='order_view'),
]

