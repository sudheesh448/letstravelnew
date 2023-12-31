from django.urls import path
from . import views



from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:category_id>/', views.home, name='home'),
    
    path('productdetails/<slug:slug>/', views.productdetails, name='productdetails'),
    path('getcolorids/', views.getcolorids, name='getcolorids'),
    path('getcolorname/', views.getcolorname, name='getcolorname'),
    path('shop/', views.shop, name='shop'),
    path('shop/<int:category_id>/', views.shop, name='shop'),
    path('shop_filter/', views.shop_filter, name='shop_filter'), 
]
