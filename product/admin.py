from django.contrib import admin

# Register your models here.
from .models import Produit ,order ,Category, Cart,ProductImage  , savelist, Likeprod , Color , Size , Brand , ProductAttr,PaymentHistory


admin.site.register(order)
admin.site.register(PaymentHistory)
admin.site.register(ProductImage)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Brand)
admin.site.register(Cart)
admin.site.register(savelist)
admin.site.register(Likeprod)
admin.site.register(Category)
@admin.register(Produit)
class prodModelAdmin(admin.ModelAdmin):
    list_display=["id","name","likes","category","image_tag","status"]
    list_editable =("status",)


class PayPalTransactionAdmin(admin.ModelAdmin):
    list_display = ('txn_id', 'user', 'product', 'amount', 'payment_status', 'created_at')
    search_fields = ('txn_id', 'payer_email')    


admin.site.register(ProductAttr)    
