
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('custm.urls')),
     path('', include('paypal.standard.ipn.urls')),
       path('product', include('product.urls')),
          path('accounts/', include('allauth.urls')),  # or your app's URL patterns
]
handler404='product.views.error_404'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
