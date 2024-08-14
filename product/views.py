import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views import View
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings as se
from django.core.mail import send_mail
from django import forms

from .models import prod, PQU, order
from custm.models import clien

def seemore(request, slug):
    """Displays the detail page of a specific product."""
    produ = get_object_or_404(prod, slug=slug)
    context = {'pro': produ}
    return render(request, 'detailspro.html', context)

def ajoutcar(request, slug):
    """Adds a product to the cart or updates the quantity if already in the cart."""
    user = request.user
    product = get_object_or_404(prod, slug=slug)
    cart, _ = PQU.objects.get_or_create(user=user)
    order_instance, created = order.objects.get_or_create(user=user, produit=product)

    if created:
        cart.orders.add(order_instance)
    else:
        order_instance.quantiti += 1
        order_instance.save()

    return redirect(reverse("home"))  # Replace 'home' with your desired redirect URL name

def delet(request, slug):
    """Deletes a product from the cart based on its slug."""
    if request.method == 'POST':
        try:
            product = get_object_or_404(prod, slug=slug)
            cart = get_object_or_404(PQU, user=request.user)
            order_to_delete = cart.orders.filter(produit=product).first()

            if order_to_delete:
                cart.orders.remove(order_to_delete)
                order_to_delete.delete()
                message = 'Product successfully removed from cart.'
            else:
                message = 'Product not found in your cart.'

        except Exception as e:
            message = f'Error occurred: {str(e)}'

        return redirect('checkout')  # Replace with the actual name of your cart view

class Category(View):
    """Displays products based on their category."""
    def get(self, request, val):
        products = prod.objects.filter(category=val)
        context = {'product': products}
        return render(request, "category.html", context)

def update_quantity(request, order_id):
    """Updates the quantity of an order or deletes the order if quantity is zero."""
    if request.method == "POST":
        order_instance = get_object_or_404(order, id=order_id)
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            order_instance.quantiti = new_quantity
            order_instance.save()
        else:
            order_instance.delete()
    return redirect('checkout')  # Adjust redirect target as needed

# views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings as se
from .models import prod, order

class checkout1(View):
    """Displays the checkout page for a specific product."""
    def get(self, request, slug):
        user = request.user
        order_instance = get_object_or_404(prod, slug=slug)
        amount = order_instance.prix
        total = amount + 23  # Add shipping cost
        host = request.get_host()

        # Create or retrieve an order record
        order_record, created = order.objects.get_or_create(
            user=user,
            produit=order_instance,
            defaults={
                'quantiti': 1,  # Set a default value if needed
                'status': 'Pending'
            }
        )

        # Update the order with amount and total if they are relevant fields
        if created:
            order_record.amount = amount
            order_record.total = total
            order_record.save()

        paypal_data = {
            "business": se.PAYPAL_RECEIVER_EMAIL,
            "amount": f"{total:.2f}",
            "item_name": order_instance.name,
            "invoice": str(order_record.id),  # Use order ID to track the payment
            "currency_code": "USD",
            "notify_url": f"https://{host}{reverse('paypal-ipn')}",
            "return_url": f"https://{host}{reverse('payment_done', kwargs={'id': order_record.id})}",
            "cancel_url": f"https://{host}{reverse('payment_fail', kwargs={'id': order_record.id})}"
        }

        paypal = PayPalPaymentsForm(initial=paypal_data)

        return render(request, "check.html", {'paypal': paypal, 'total': total, 'order': order_instance})


def cart_summary(request):
    """Displays the user's cart summary."""
    cart = PQU.objects.filter(user=request.user).first()
    context = {}

    if cart:
        orders = cart.orders.all()
        amount = sum(o.produit.prix * o.quantiti for o in orders)
        total = amount + 23  # Add shipping cost

        context = {
            'orders': orders,
            'amount': amount,
            'total': total
        }
    else:
        return redirect('cart')  # Assuming you have a view to show the cart

    return render(request, "mycart.html", context)

def payment_done(request, id):
    """Handles payment success callback from PayPal."""
    payer_id = request.GET.get('PayerID')
    if not payer_id:
        return render(request, "error.html", {"message": "PayerID missing"})

    order_instance = get_object_or_404(order, id=id)
    order_instance.status = 'Paid'
    order_instance.save()

    context = {'order': order_instance, 'username': order_instance.user.username}
    return render(request, "pay_suc.html", context)

def payment_fail(request, id):
    """Handles payment failure callback from PayPal."""
    order_instance = get_object_or_404(order, id=id)
    
    context = {
        'order': order_instance,
        'message': 'Payment failed. Please try again or contact support if the issue persists.'
    }
    return render(request, "pay_fail.html", context)

def product_order_status(request, product_slug):
    """Displays the order status for a specific product."""
    product = get_object_or_404(prod, slug=product_slug)
    orders = order.objects.filter(produit=product)

    context = {
        'product': product,
        'orders': orders
    }
    return render(request, "product_order_status.html", context)

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

def contact_us(request):
    """Handles contact form submission and sends an email."""
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
                recipient_list=[se.DEFAULT_FROM_EMAIL],
            )
            
            return render(request, 'contact_success.html', {'name': name})
    else:
        form = ContactForm()
    
    return render(request, 'contact_us.html', {'form': form})

def orders_to_deliver(request):
    """Fetches orders that are paid but not shipped."""
    orders = order.objects.filter(status='Paid').exclude(status='Shipped')
    context = {'orders': orders}
    return render(request, 'orders_to_deliver.html', context)

from django.http import HttpResponse
from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver

@receiver(valid_ipn_received)
def handle_ipn(sender, **kwargs):
    """Handles PayPal IPN notifications."""
    ipn_obj = sender
    if ipn_obj.payment_status == 'Completed':
        order_id = ipn_obj.invoice
        order_instance = order.objects.filter(id=order_id).first()
        if order_instance:
            order_instance.status = 'Paid'
            order_instance.save()

    return HttpResponse("IPN processed")
