from django.contrib import admin

# Register your models here

from django.contrib import admin


from . models import users , userADRESS

admin.site.register(users)
admin.site.register(userADRESS)