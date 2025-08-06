from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from cloudinary.models import CloudinaryField

from django.utils.html import mark_safe
from custm.models import userADRESS
# Fonction pour obtenir le temps actuel
def current_time():
    return timezone.now()
class Banner (models.Model):
    img = models.CharField(max_length=200)
    alt_text=models.CharField(max_length=3000)

# Modèle pour les images de produits
class ProductImage(models.Model):
    image = CloudinaryField('image')
    

    def __str__(self):
        return self.image.url
class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7) 
    

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name    
    
class Brand(models.Model):
    name = models.CharField(max_length=10)  
    image = CloudinaryField('image')
class Category(models.Model):
    name = models.CharField(max_length=200)
    image = CloudinaryField('image')
    def __str__(self):
        return self.name


    
# Modèle pour les produits
class Produit(models.Model):
    CATEGORY_CHOICES = [
        ("jewellery", "jewellery"),
        ("man", "manclothes"),
        ("women", "womenclothes"),
        ("other", "other"),
        ("football", "football"),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
  
    stock = models.IntegerField()
    image = CloudinaryField('image')
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    description = models.TextField(max_length=2000)
    images = models.ManyToManyField(ProductImage, blank=True)  # Lien vers les images du produit
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    colors = models.ManyToManyField(Color)
    sizes = models.ManyToManyField(Size)
    status=models.BooleanField(default=True)
    price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
     
    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" /> ' % (self.image.url))
    def __str__(self):
        return self.image.url if self.image else "No Image"  
    def get_absolute_url(self):
        return reverse("seemore", kwargs={"slug": self.slug})
class ProductAttr(models.Model):
    product=models.ForeignKey(Produit, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
   

    def __str__(self):
        return self.product.name
# Modèle pour les transactions PayPal



# Modèle pour les commandes
class order(models.Model):
    PENDING = "P"
    COMPLETED = "D"
    FAILED = "F"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (COMPLETED, "delevred"),
        (FAILED, "Failed"),
    )
   
  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    adress=models.ForeignKey(userADRESS, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantiti = models.PositiveIntegerField(default=1)
    status=models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Montant de la commande
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total de la commande

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

# Modèle pour le panier
class Cart(models.Model):
    user =models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    orders = models.ManyToManyField(order)  
 
    created_at = models.DateTimeField(default=current_time)

    def __str__(self):
        return self.user.username




# Modèle pour les listes de souhaits
class savelist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s wishlist"

# Modèle pour les likes de produits
class Likeprod(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    is_like = models.BooleanField(default=True) # New field to track if it's a like or a dislike
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} liked {self.produit.name}"

class PaymentHistory(models.Model):
    PENDING = "P"
    COMPLETED = "C"
    FAILED = "F"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ooder = models.ForeignKey(Cart, on_delete=models.CASCADE)
    stripe_payment_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    address = models.ForeignKey(userADRESS, on_delete=models.SET_NULL, null=True, blank=True)  # Lien vers l'adresse
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantiti = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment of {self.amount} for order {self.user}"
