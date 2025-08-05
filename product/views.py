import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views import View
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings as se
from django.core.mail import send_mail
from django import forms

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views import View
from .models import  userADRESS, PaymentHistory
import stripe
from django.conf import settings
from .models import Produit, Cart, order, savelist, Likeprod  , Category
from custm.models import userADRESS
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")


@login_required
def get_cart(request):
    user = request.user
    # Retrieve the user's cart
    cart = Cart.objects.filter(user=user).first()
    
    # Check if the cart is empty
    if not cart or not cart.orders.exists():
        return render(request, "cart_empty.html")

    # Retrieve all orders in the cart
    orders = cart.orders.all()
    
    # Calculate total amount based on product price and quantity
    amount = sum(
        order.produit.price * order.quantiti
        for order in orders
    )
    shipping_cost = 23  # Fixed shipping cost
    total = amount + shipping_cost  # Total cost including shipping

    # Pass relevant context to the template
    context = {
        'orders': orders,
        'amount': amount,
        'shipping_cost': shipping_cost,
        'total': total
    }

    return render(request, 'mycart.html', context)



def seemore(request, slug):
    produ = get_object_or_404(Produit, slug=slug)
    related=Produit.objects.filter(category=produ.category).exclude(slug=slug)
    context = {'pro': produ,'rel':related}
    return render(request, 'detailspro.html', context)




from django.http import HttpResponseNotAllowed

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

@login_required
def ajoutcar(request, slug):
   
        
        user = request.user
        adress = userADRESS.objects.filter(user=user).first()
        
        if adress:
            product = get_object_or_404(Produit, slug=slug)
            cart, _ = Cart.objects.get_or_create(user=user)
            
            # Try to get the order if it exists, otherwise create a new one
            order_instance, created = order.objects.get_or_create(
                user=user, produit=product, adress=adress,
                  # Default quantity to 0 for new orders
            )
            
            # Increment the quantity and calculate the total
            order_instance.quantiti += 1
            order_instance.amount = product.price
            order_instance.total = order_instance.amount * order_instance.quantiti
            order_instance.save()

            # Add the order to the cart if it's new
            if created:
                cart.orders.add(order_instance)

            return redirect(reverse("home"))
        else:
            return redirect("adress")
   









@login_required
def delet(request, slug):
    if request.method == 'POST':
        product = get_object_or_404(Produit, slug=slug)
        cart = get_object_or_404(Cart, user=request.user)
        order_to_delete = cart.orders.filter(produit=product).first()
        ord=order.objects.filter(user=request.user)
        if order_to_delete:
            cart.orders.remove(order_to_delete)
            ord.delete
            order_to_delete.delete()

        return redirect('home')
from django.views.decorators.csrf import csrf_exempt

def category (req):
    data = Category.objects.all()
   
    return render (req,'categoryprod.html',locals())
def category_prod (req,val):
    data = Category.objects.get(name=val)
    prod=Produit.objects.filter(category=data)
    return render (req,'category.html',locals())

@login_required
def update_quantity(request, order_id):
    if request.method == "POST":
        order_instance = get_object_or_404(order, id=order_id)
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            order_instance.quantiti = new_quantity
            order_instance.save()
        else:
            order_instance.delete()
    return redirect('cart')

import stripe

from django.shortcuts import render, redirect
from paypal.standard.forms import PayPalPaymentsForm








@login_required
def cancel_payment(request):
      return render(request, 'pay_fail .html')
   
@login_required
def sucess_payment(request):
    
    return render(request, "pay_suc.html")
@login_required
def product_order_status(request, product_slug):
    product = get_object_or_404(Produit, slug=product_slug)
    orders = order.objects.filter(produit=product)
    user = request.user

    context = {'product': product, 'orders': orders}
    return render(request, "product_order_status.html", context)
from djangotest.settings import EMAIL_HOST_USER
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            send_mail(
                subject=f"Contact Us Message from {name}",
                message=message,
                from_email=email,
                recipient_list=[se.EMAIL_HOST_USER],
            )
            return render(request, 'contact_success.html', {'name': name})
    else:
        form = ContactForm()
    
    return render(request, 'contact_us.html', {'form': form})




from django.http import HttpResponse
from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from djangotest.settings import AUTH_USER_MODEL

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import  Cart
import stripe

from django.conf import settings




from custm.form import SearchForm

def search(request):
    form = SearchForm(request.GET or None)
    products = []
    
    if form.is_valid():
        query = form.cleaned_data['query']
        products = Produit.objects.filter(name__icontains=query)
    
    context = {'form': form, 'products': products}
    return render(request, 'search.html', context)
@login_required
def saveprod(req, slug):
    user = req.user
    post = get_object_or_404(Produit, slug=slug)
    like = savelist.objects.filter(produit=post, user=user).first()

    if like:
        like.delete()
    else:
        savelist.objects.create(produit=post, user=user)

    return redirect("home")
@login_required
def deletesa(request, slug):
    if request.method == 'POST':
        user = request.user
        post = get_object_or_404(Produit, slug=slug)
        like = savelist.objects.filter(produit=post, user=user).first()
        like.delete()

    return redirect('home')
  # Request method not allowed





from custm.form import SearchForm

def search(request):
    form = SearchForm(request.GET or None)  # Crée une instance du formulaire avec les données de la requête
    products = []  # Liste pour stocker les produits trouvés
    query = ""  # Variable pour stocker la requête de recherche

    if form.is_valid():  # Vérifie si le formulaire est valide
        query = form.cleaned_data['query']  # Récupère la requête de recherche
        products = Produit.objects.filter(name__startswith=query)  # Filtre les produits dont le nom commence par la requête

    context = {
        'form': form,
        'products': products,
        'query': query  # Ajoute la requête à context pour l'affichage
    }
    return render(request, 'search.html', context) 
@login_required
def saveprod(req, slug):
    user = req.user
    post = get_object_or_404(Produit, slug=slug)
    like = savelist.objects.filter(produit=post, user=user).first()

    if like:
        like.delete()
    else:
        savelist.objects.create(produit=post, user=user)

    return redirect("home")
@login_required
def getsave(req):
    user = req.user
    pos=savelist.objects.all()
    return render(req, 'save.html', locals()) 
@login_required
def LikePos(req, pk):
    user = req.user
    pr = get_object_or_404(Produit, id=pk)
  
    like = Likeprod.objects.filter(produit=pr, user=user).first()

    if like:
        like.delete()
        pr.likes -= 1
        liked = False  # Change to False when disliked
    else:
        Likeprod.objects.create(produit=pr, user=user)
        pr.likes += 1
        liked = True  # Change to True when liked

    pr.save()

    # Return a JSON response instead of redirect
    return JsonResponse({
        'liked': liked,
        'likes_count': pr.likes
    })
# views.py


from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from .models import Produit, order, Cart
from django.urls import reverse


def product_list(req):
    po=Produit.objects.all()
    return render(req,"prod_list.html",locals())







from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views import View
from django.http import HttpResponseRedirect
import stripe
from .models import order, userADRESS

from django.views import View
from django.http import JsonResponse
import stripe
from .models import Cart, userADRESS  # Assurez-vous que les modèles sont correctement importés

# Remplacez par votre clé secrète Stripe


from django.http import JsonResponse
from django.views import View
import stripe
import json







from django.views.decorators.http import require_GET
def cancel(request):
    return render(request, 'cancel.html')

@require_GET
@login_required
def success(request):
    # Here you can update the payment status to completed
    payment_history = PaymentHistory.objects.filter(stripe_payment_id=request.GET.get('session_id')).first()
    
    if payment_history:
        payment_history.payment_status = PaymentHistory.COMPLETED
        payment_history.save()
    
    return render(request, 'success.html', {'payment_history': payment_history})

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
import stripe
import json
from .models import Cart


import json
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
import stripe
from .models import Cart  # Assuming you're using a Cart model

 # Replace with your actual Stripe secret key

class CreateStripeCheckoutSessionView(View):
    def post(self, request ):
        # Ensure the correct cart/order is fetched
       
        data = json.loads(request.body)
        quantity = data.get('quantity')
        address = data.get('address')

        # Calculate total amount (replace with your actual logic)
        product_price = 2000  # Example product price in cents
        total_amount = product_price * quantity

        # Create a Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price':'prod_Qx8eOju0TsIoie' ,
                'quantity': 1
            }],
            mode='payment',
            success_url='http://127.0.0.1:8000/success/',
            cancel_url='http://127.0.0.1:8000/cancel/',
        )

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Cart, PaymentHistory
import stripe
from django.conf import settings



from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import stripe



@login_required
def checkout_view(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    
    if not cart or not cart.orders.exists():
        return redirect('get_cart')  # Redirect to cart if it's empty

    orders = cart.orders.all()
    amount = sum(
        order.produit.price * order.quantiti 
        for order in orders
    )
    shipping_cost = 23  # Fixed shipping cost
    total = amount + shipping_cost  # Total cost including shipping
    amount_in_cents = int(total * 100)  # Convert total to cents

    if request.method == 'POST':
        YOUR_DOMAIN = "http://localhost:8000"  # Change this to your domain in production
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Total Cart Amount',
                        },
                        'unit_amount': amount_in_cents,  # Amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/productsuccess/',
            cancel_url=YOUR_DOMAIN + '/productcancel/',
        )

        # Save payment history
        
        PaymentHistory.objects.create(
            user=user,
            amount=total,
            stripe_payment_id=checkout_session.id,
            ooder=cart,
            payment_status="C"
        )
       
        return redirect(checkout_session.url)  # Redirect to Stripe Checkout page
       
    context = {
        'orders': orders,
        'amount': amount,
        'shipping_cost': shipping_cost,
        'total': total,
        'stripe_public_key': stripe.api_key  # Ensure you have this in your settings
    }
   
    return render(request, 'checkout.html', context)








stripe.api_key = "sk_test_51Q5E4gADfWjSfslWFg3RJj3zAf5KjMVLwOYgaP86HFdNmAM3XIEogcKPEZmZaWDc9rw5tkX4BS5BU690Npb5J62s00dY5JaDSt"


