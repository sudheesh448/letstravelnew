from django.urls import path

from . import customer_view

from . import views
from . import product_view_add_category



urlpatterns = [
    path('adminlogin', views.adminlogin, name='adminlogin'),

    path('addproduct/', views.add_product, name='add_product'),
    path('get_color_checkboxes/', views.get_color_checkboxes, name='get_color_checkboxes'),
    
    path('saveproductvariantcolor/', views.save_product_variant_color, name='save_product_variant_color'),
    path('uploadimages/<int:product_variant_color_id>/', views.upload_images, name='upload_images'),


    path('dashboard/', views.dashboard, name='dashboard'),
    path('adminlogout/', views.admin_logout, name='admin_logout'),
    
    
    path('addcategory/', product_view_add_category.add_category, name='addcategory'),
    path('addvariants/', product_view_add_category.addvariants, name='addvariants'),
    path('categoryview/', product_view_add_category.category_view, name='categoryview'),
    path('categoryupdate/<int:category_id>/', product_view_add_category.category_update, name='category_update'),


    path('productlist/', product_view_add_category.productlist, name='productlist'),
    path('viewproduct/<int:product_id>/', product_view_add_category.viewproduct, name='viewproduct'),
    path('mark_variant_deleted/', product_view_add_category.mark_variant_deleted, name='mark_variant_deleted'),
    path('mark_variant_revoked/', product_view_add_category.mark_variant_revoked, name='mark_variant_revoked'),
    path('update_price_stock/', product_view_add_category.update_price_stock, name='update_price_stock'),
    path('add_new_variant/', product_view_add_category.add_new_variant, name='add_new_variant'),

   

    path('customerlist/', customer_view.customer_list, name='customerlist'),

    path('editproduct/<int:product_id>/', customer_view.editproduct, name='edit_product'),
    path('deleteproduct/<int:product_id>/', customer_view.delete_product, name='delete_product'),
    path('revokeproduct/<int:product_id>/', customer_view.revoke_product, name='revoke_product'),
    path('viewcustomer/<int:customer_id>/', customer_view.viewcustomer, name='viewcustomer'),
    path('bancustomer/<int:customer_id>/', customer_view.bancustomer, name='bancustomer'),
    path('deletecustomer/<int:customer_id>/', customer_view.deletecustomer, name='deletecustomer'),
    path('unbancustomer/<int:customer_id>/', customer_view.unbancustomer, name='unbancustomer'),
    path('revokecustomer/<int:customer_id>/', customer_view.revokecustomer, name='revokecustomer'),

    path('ordertableadmin',product_view_add_category.ordertableadmin,name="ordertableadmin"),
    path('cancel_orders_admin/<int:order_id>', product_view_add_category.cancel_orders_admin, name='cancel_orders_admin'), 
    path('order_viewadmin/<int:order_id>',product_view_add_category.order_viewadmin,name='order_viewadmin'),
    path('Shipped_order/<int:order_id>',product_view_add_category.Shipped_order,name='Shipped_order'), 
    path('Delivered_order/<int:order_id>',product_view_add_category.Delivered_order,name='Delivered_order'),


    path('revenue_chart_data/', views.revenue_chart_data, name='revenue_chart_data'), 
    path('payment_chart_data/', views.payment_chart_data, name='payment_chart_data'), 
    path('order_status_chart_data/', views.order_status_chart_data, name='order_status_chart_data'), 
    path('revenue_chart_line/', views.revenue_chart_line, name='revenue_chart_line'), 
    path('sales_report_view/', views.sales_report_view, name='sales_report_view'), 
   
    path('delete_image/', product_view_add_category.delete_image, name='delete_image'),
    ]


