from django.contrib import admin

# Register your models here.
from . models import prod ,order,DELES , PQU , Payment , savelist


admin.site.register(order)
admin.site.register(DELES)
admin.site.register(Payment)
admin.site.register(PQU)
admin.site.register(savelist)
@admin.register(prod)
class prodModelAdmin(admin.ModelAdmin):
    list_display=["id","name","prix","image"]
