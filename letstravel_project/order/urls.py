from django.urls import path
from . import views


urlpatterns = [
    path('cod/',views.cod,name='cod'),
    path('place_order/<int:add_user_id>',views.place_order,name='place_order'),
    path('ordertable',views.ordertable,name="ordertable"),
    path('order_view/<int:order_id>',views.order_view,name='order_view'),
    path('cancel_orders/<int:order_id>',views.cancel_orders,name='cancel_orders'), 
    path('online_payment_order/<int:user_add_id>',views.online_payment_order,name='online_payment_order'),
    path('pay_now/',views.pay_now,name='pay_now'),
    path('initiate_payment/',views.initiate_payment,name='initiate_payment'),
    path('order_success/',views.order_success,name='order_success'),
    path('pay_using_wallet/',views.pay_using_wallet,name='pay_using_wallet'),
    path('view_wallets/',views.view_wallets,name='view_wallets'),
    path('generate_invoice/<int:order_id>/',views.generate_invoice,name='generate_invoice'),    
]

