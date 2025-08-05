import uuid
import os

import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings as se
from django.core.mail import send_mail
from django import forms
from django.views.decorators.http import require_GET
from paypal.standard.forms import PayPalPaymentsForm
from dotenv import load_dotenv

from .models import Produit, Cart, order, savelist, Likeprod, Category, userADRESS, PaymentHistory
from custm.models import userADRESS # (Assuming custm is another app, otherwise this is a duplicate)
from custm.form import SearchForm # (Assuming custm is another app, otherwise this is a duplicate)


# Load environment variables from .env file


logger = logging.getLogger(__name__)

# --- Product & Category Views ---

def product_list(request):
    po = Produit.objects.all()
    # You might want to prefetch related data for performance, e.g.,
    # po = Produit.objects.all().prefetch_related('likeprod_set')
    return render(request, "prod_list.html", {'po': po})

def seemore(request, slug):
    produ = get_object_or_404(Produit, slug=slug)
    related = Produit.objects.filter(category=produ.category).exclude(slug=slug)
    context = {'pro': produ, 'rel': related}
    return render(request, 'detailspro.html', context)

def category(request):
    data = Category.objects.all()
    return render(request, 'categoryprod.html', {'data': data})

def category_prod(request, val):
    data = get_object_or_404(Category, name=val)
    prod = Produit.objects.filter(category=data)
    return render(request, 'category.html', {'prod': prod, 'data': data})

def search(request):
    form = SearchForm(request.GET or None)
    products = []
    query = ""

    if form.is_valid():
        query = form.cleaned_data['query']
        products = Produit.objects.filter(name__icontains=query)

    context = {
        'form': form,
        'products': products,
        'query': query
    }
    return render(request, 'search.html', context)

# --- Cart & Order Management ---

@login_required
def get_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    
    if not cart or not cart.orders.exists():
        return render(request, "cart_empty.html")

    orders = cart.orders.all()
    amount = sum(order_item.produit.price * order_item.quantiti for order_item in orders)
    shipping_cost = 23
    total = amount + shipping_cost

    context = {
        'orders': orders,
        'amount': amount,
        'shipping_cost': shipping_cost,
        'total': total
    }
    return render(request, 'mycart.html', context)

@login_required
def ajoutcar(request, slug):
    user = request.user
    adress = userADRESS.objects.filter(user=user).first()
    
    if not adress:
        return redirect("adress")
    
    product = get_object_or_404(Produit, slug=slug)
    cart, _ = Cart.objects.get_or_create(user=user)
    
    order_instance, created = order.objects.get_or_create(
        user=user, produit=product, adress=adress
    )
    
    if not created:
        order_instance.quantiti += 1
    else:
        order_instance.quantiti = 1

    order_instance.amount = product.price
    order_instance.total = order_instance.amount * order_instance.quantiti
    order_instance.save()
    
    if created:
        cart.orders.add(order_instance)

    return redirect(reverse("cart"))

@login_required
def delet(request, slug):
    if request.method == 'POST':
        product = get_object_or_404(Produit, slug=slug)
        cart = get_object_or_404(Cart, user=request.user)
        order_to_delete = cart.orders.filter(produit=product).first()
        
        if order_to_delete:
            cart.orders.remove(order_to_delete)
            order_to_delete.delete()

    return redirect('cart')

@login_required
def update_quantity(request, order_id):
    if request.method == "POST":
        order_instance = get_object_or_404(order, id=order_id, user=request.user)
        new_quantity = int(request.POST.get('quantity', 1))
        
        if new_quantity > 0:
            order_instance.quantiti = new_quantity
            order_instance.total = order_instance.produit.price * new_quantity
            order_instance.save()
        else:
            order_instance.delete()
    return redirect('cart')

# --- User Actions ---

@login_required
def saveprod(request, slug):
    user = request.user
    post = get_object_or_404(Produit, slug=slug)
    like, created = savelist.objects.get_or_create(produit=post, user=user)

    if not created:
        like.delete()

    return redirect("home")

@login_required
def getsave(request):
    user = request.user
    pos = savelist.objects.filter(user=user)
    return render(request, 'save.html', {'pos': pos})

@login_required
def deletesa(request, slug):
    if request.method == 'POST':
        user = request.user
        post = get_object_or_404(Produit, slug=slug)
        like = get_object_or_404(savelist, produit=post, user=user)
        like.delete()
    return redirect('home')

@login_required
def LikePos(request, pk):
    user = request.user
    product = get_object_or_404(Produit, id=pk)
    
    liked_obj, created = Likeprod.objects.get_or_create(produit=product, user=user)

    if not created:
        liked_obj.delete()
        product.likes -= 1
        liked = False
    else:
        product.likes += 1
        liked = True

    product.save()

    return JsonResponse({
        'liked': liked,
        'likes_count': product.likes
    })

# --- Payment & Checkout ---

@login_required
def checkout_view(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    
    if not cart or not cart.orders.exists():
        return redirect('get_cart')

    orders = cart.orders.all()
    amount = sum(order_item.produit.price * order_item.quantiti for order_item in orders)
    shipping_cost = 23
    total = amount + shipping_cost
    amount_in_cents = int(total * 100)

    if request.method == 'POST':
        YOUR_DOMAIN = "http://localhost:8000"
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Total Cart Amount'},
                    'unit_amount': amount_in_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=YOUR_DOMAIN + reverse('success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=YOUR_DOMAIN + reverse('cancel'),
        )
        return redirect(checkout_session.url, code=303)
    
    context = {
        'orders': orders,
        'amount': amount,
        'shipping_cost': shipping_cost,
        'total': total,
        'stripe_public_key': STRIPE_PUBLIC_KEY,
    }
    return render(request, 'checkout.html', context)


@login_required
@require_GET
def success(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()

    if not cart:
        logger.error(f"No cart found for user: {user.id}")
        return redirect('get_cart')

    session_id = request.GET.get('session_id')
    
    if not session_id:
        logger.error(f"No session_id in the request for user: {user.id}")
        return render(request, 'error.html', {'message': 'No session ID provided.'})

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status != 'paid':
            logger.error(f"Payment not successful for session_id: {session_id}")
            return render(request, 'error.html', {'message': 'Payment not successful.'})
        
        total_amount = sum(order_item.produit.price * order_item.quantiti for order_item in cart.orders.all())

        for order_item in cart.orders.all():
            PaymentHistory.objects.create(
                user=user,
                amount=total_amount,
                stripe_payment_id=session_id,
                payment_status="C",
                ooder=cart,
                produit=order_item.produit,
                quantiti=order_item.quantiti,
                price=order_item.produit.price
            )

        cart.orders.all().delete()
        cart.delete()
        
        return render(request, 'success.html', {'session': session})

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error for session_id: {session_id}, error: {e.user_message}")
        return render(request, 'error.html', {'message': f"Stripe error: {e.user_message}"})
    except Exception as e:
        logger.error(f"Unexpected error for user: {user.id}, error: {str(e)}")
        return render(request, 'error.html', {'message': f"An error occurred: {str(e)}"})

@require_GET
def cancel(request):
    return render(request, 'cancel.html')

def previceh(request):
    return render(request, "previce.html")
    
# --- Other Views ---

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

def error_404(request, exception):
    return render(request, '404.html', {})




# views.py (Fixed Version)

import uuid
import os

import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings as se
from django.core.mail import send_mail
from django import forms
from django.views.decorators.http import require_GET
from paypal.standard.forms import PayPalPaymentsForm
from dotenv import load_dotenv

from .models import Produit, Cart, order, savelist, Likeprod, Category, userADRESS, PaymentHistory
from custm.models import userADRESS 
from custm.form import SearchForm

# Load environment variables from .env file


logger = logging.getLogger(__name__)

# --- Product & Category Views ---

def product_list(request):
    products = Produit.objects.all()
    
    # Check if the user is authenticated and annotate each product with a "user_liked" status
    if request.user.is_authenticated:
        for product in products:
            product.user_liked = Likeprod.objects.filter(produit=product, user=request.user).exists()
    else:
        # For anonymous users, set user_liked to False for all products
        for product in products:
            product.user_liked = False
            
    context = {
        'po': products
    }
    return render(request, "prod_list.html", context)

def seemore(request, slug):
    produ = get_object_or_404(Produit, slug=slug)
    related = Produit.objects.filter(category=produ.category).exclude(slug=slug)
    
    # Also check the like status for the detailed product and related products
    if request.user.is_authenticated:
        produ.user_liked = Likeprod.objects.filter(produit=produ, user=request.user).exists()
        for related_prod in related:
            related_prod.user_liked = Likeprod.objects.filter(produit=related_prod, user=request.user).exists()
    else:
        produ.user_liked = False
        for related_prod in related:
            related_prod.user_liked = False

    context = {'pro': produ, 'rel': related}
    return render(request, 'detailspro.html', context)

# ... (The rest of your views.py file remains the same) ...

# --- User Actions ---
# ...
@login_required
def LikePos(request, pk):
    user = request.user
    product = get_object_or_404(Produit, id=pk)
    
    liked_obj, created = Likeprod.objects.get_or_create(produit=product, user=user)

    if not created:
        liked_obj.delete()
        product.likes -= 1
        liked = False
    else:
        product.likes += 1
        liked = True

    product.save()

    return JsonResponse({
        'liked': liked,
        'likes_count': product.likes
    })
# ...    


# views.py

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Produit, Likeprod

def product_list(request):
    products = Produit.objects.all()
    
    if request.user.is_authenticated:
        for product in products:
            # Check the user's like/dislike status and store it on the product object
            like_status = Likeprod.objects.filter(produit=product, user=request.user).first()
            if like_status:
                product.user_liked = like_status.is_like
            else:
                product.user_liked = None  # None indicates no action has been taken
    else:
        for product in products:
            product.user_liked = None
            
    context = {'po': products}
    return render(request, "prod_list.html", context)

@login_required
def LikePos(request, pk):
    product = get_object_or_404(Produit, id=pk)
    user = request.user
    action = request.POST.get('action')

    # Find if a like/dislike record already exists for the user and product
    existing_action = Likeprod.objects.filter(produit=product, user=user).first()

    if action == 'like':
        if existing_action and existing_action.is_like:
            # User already liked, so remove the like
            existing_action.delete()
            product.likes -= 1
        elif existing_action and not existing_action.is_like:
            # User disliked, now they like. Switch action.
            existing_action.is_like = True
            existing_action.save()
            product.likes += 1
            product.dislikes -= 1
        elif not existing_action:
            # No action taken yet, so create a new like
            Likeprod.objects.create(produit=product, user=user, is_like=True)
            product.likes += 1
    
    elif action == 'dislike':
        if existing_action and not existing_action.is_like:
            # User already disliked, so remove the dislike
            existing_action.delete()
            product.dislikes -= 1
        elif existing_action and existing_action.is_like:
            # User liked, now they dislike. Switch action.
            existing_action.is_like = False
            existing_action.save()
            product.dislikes += 1
            product.likes -= 1
        elif not existing_action:
            # No action taken yet, so create a new dislike
            Likeprod.objects.create(produit=product, user=user, is_like=False)
            product.dislikes += 1

    product.save()

    return JsonResponse({
        'likes': product.likes,
        'dislikes': product.dislikes,
        'user_liked': action == 'like'
    })