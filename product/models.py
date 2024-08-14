from django.db import models
from django.urls import reverse
from djangotest.settings import AUTH_USER_MODEL
import datetime
from django.utils import timezone
from custm.models import clien
def current_time():
    return timezone.now()
# Create your models here.
class prod(models.Model):

    x=(("jewellery" , "jewellery "),
       ("man" , "manclothes "),
       ("women" , "womenclothes ")
      
       )
    
    name=models.CharField()
    slug=models.SlugField(max_length=200 , default=1 , unique=True)
    prix=models.DecimalField(max_digits=122,decimal_places=2)
    stock=models.IntegerField()
    image=models.ImageField(upload_to="photos/%y/%m/%d")
    category=models.CharField(max_length=20,blank=True,choices=x)
   
    description=models.TextField(max_length=2000)
    def __str__ (self):
         return self.name
    def get_absolute_url(self):
          return reverse("seemore", kwargs={"slug":self.slug})


     

class Payment(models.Model):
    user=user= models.OneToOneField(AUTH_USER_MODEL , on_delete=models.CASCADE) ,
    amount=models.FloatField()
    maro_pay_order_id=models.CharField(blank=True,null=True ,max_length=50)
    maro_pay_payment_stat=models.CharField( blank=True,null=True ,max_length=50)
    maro_pay_payment_id=models.CharField( blank=True,null=True ,max_length=50)
    paid=models.BooleanField(default=False)

from django.db import models
from django.contrib.auth.models import User

class order(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    produit = models.ForeignKey(prod, on_delete=models.CASCADE)
    quantiti = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, default='Pending')  # Ajouter un champ status

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

     
from django.db import models

class DELE(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
    ]

    # models.py
from django.db import models

class DELES(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    produit = models.ForeignKey(prod, on_delete=models.CASCADE)
    quantiti = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Shipped', 'Shipped')])
    # Add the missing fields
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class PQU(models.Model):
     user= models.OneToOneField(AUTH_USER_MODEL , on_delete=models.CASCADE) 
     orders= models.ManyToManyField(order )  
     created_at = models.DateTimeField(default=current_time)

     def __str__ (self):
         return self.user.username
    
class savelist(models.Model):
     user= models.ForeignKey(AUTH_USER_MODEL , on_delete=models.CASCADE) 
     produit= models.ForeignKey(prod , on_delete=models.CASCADE)
    