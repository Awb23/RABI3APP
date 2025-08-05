from django.urls import path
from . import views


from django.views.generic import TemplateView
urlpatterns = [
   
# urls.py

    
    # Other URLs...


       

   

# For IPN

   
   

    

path('update-quantity/<int:order_id>/', views.update_quantity, name='update_quantity'),


path("<str:slug>",views.seemore,name="seemore" ),
 path('add-to-cart/<slug:slug>/',views.ajoutcar, name='ajoute'),
path('contact/',views.contact_us, name='contact_us'),
path('delete/<slug:slug>/', views.delet, name='delete'),
path('deletesave/<slug:slug>/', views.deletesa, name='savete'),
path('save/<slug:slug>/', views.saveprod, name='save'),
path('checkout/',views.checkout_view, name='checkout'),

path("like/<str:pk>",views.LikePos,name="like" ),
path('productmycart/', views.get_cart, name='cart'),
path('category/', views.category, name='category'), 

    path('success/', views.success, name='checkout_success'),
    path('cancel/', views.cancel, name='cancel'),
path('category/<str:val>', views.category_prod, name='category_prod'), 
 
path('prodlist/', views.product_list, name='prodlist'), 

path('mywish/', views.getsave, name='getsave'), 


    # autres URL...


    path('payment/success/<int:id>/', 
         TemplateView.as_view(template_name='payment_success.html'), 
         name='success_payment'),  # Correct the spelling here
         
    path('payment/cancel/<int:id>/', 
         TemplateView.as_view(template_name='payment_cancel.html'), 
         name='cancel_payment'),

   
   
    
  
  
]

