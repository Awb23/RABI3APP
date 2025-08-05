from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError
from djangotest.settings import AUTH_USER_MODEL
x=(("agadir","agadir"),
   ("rabat","rabat"),
   ("marrakech","marakech"))
# Create your models here.
class users(AbstractUser):
    age=models.CharField( max_length=50)
    email=models.EmailField( max_length=254 , unique=True)
  


class clien(models.Model):
    user=models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE , blank=True)
    firstname=models.CharField( max_length=50)
    lastname=models.CharField( max_length=50)
    phone=models.IntegerField()
    adress=models.TextField(max_length=200)
    country=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    zipcode=models.IntegerField()
    state=models.CharField(choices=x, max_length=50)
    def __str__(self):
        return self.state 
    
   
    
   