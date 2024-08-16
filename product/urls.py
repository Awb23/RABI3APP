from django.urls import path
from . import views



urlpatterns = [
   
# urls.py

    path('product/<slug:product_slug>/order-status/',views.product_order_status, name='product_order_status'),
    path('productpaysuccess/<int:id>/',views.payment_done, name='payment_done'),
    # Other URLs...

 path('search/',views.search, name='search'),



path('update-quantity/<int:order_id>/', views.update_quantity, name='update_quantity'),

path('paysuccess/<int:id>/', views.payment_done, name='paysuc'),
path('payfial/<int:id>/', views.payment_fail, name='payment_fail'),
path("<str:slug>",views.seemore,name="seemore" ),
 path('add-to-cart/<slug:slug>/',views.ajoutcar, name='ajoute'),
path('contact/',views.contact_us, name='contact_us'),
path('delete/<slug:slug>/', views.delet, name='delete'),
path("checkout/<slug:slug>/",views.checkout1.as_view(),name="check1" ),
path("Checkout/",views.cart_summary,name="checkout" ),
path('orders-to-deliver/', views.orders_to_deliver, name='orders_to_deliver'),
path('category/<slug:val>/', views.Category.as_view(), name='category'),   


   

   
   
    
  
  
]

