from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from product.models import Produit, PaymentHistory , Cart
from custm.models import users, userADRESS
from product.models import Likeprod , Banner 
from .form import NEW, LoginForm, Profile
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes , force_str


def home(request):
    produits = Produit.objects.all()[:3]
    banner = Banner.objects.all()

    for produit in produits:
        if request.user.is_authenticated:
            produit.user_liked = Likeprod.objects.filter(produit=produit, user=request.user).exists()
        else:
            produit.user_liked = False

    context = {
        'po': produits,
        'banner': banner
    }
    return render(request, 'ap/index.html', context)

def last_product(request):
    po = Produit.objects.all().order_by('-created_at')[:3]
    return render(request, 'last_product.html', {'po': po})

@login_required
def loug(request):
    logout(request)
    return redirect("home")

from .emailv import send_verification_email

class Sign(View):
    def get(self, req):
        form = NEW()
        return render(req, "sign.html", {'form': form})

    def post(self, request):
        form = NEW(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_verification_email(user, request)
            messages.success(request, "Please check your email to activate your account.")
        else:
            messages.warning(request, "Please correct the errors below.")
        return render(request, 'sign.html', {'form': form})

class PROFILE(View):
    def get(self, req):
        form = Profile()
        return render(req, "profile.html", {'form': form})
    
    def post(self, req):
        form = Profile(req.POST)
        if form.is_valid():
            user = req.user
            clien_data = {
                'user': user,
                'zipcode': form.cleaned_data['zipcode'],
                'adress': form.cleaned_data['adress'],
                'phone': form.cleaned_data['phone'],
                'lastname': form.cleaned_data['lastname'],
                'firstname': form.cleaned_data['firstname'],
                'state': form.cleaned_data['state'],
                'city': form.cleaned_data['city'],
                'country': form.cleaned_data['country']
            }
            j = userADRESS(**clien_data)
            j.save()
            messages.success(req, "Profile updated successfully.")
            return redirect("adress")
        else:
            messages.warning(req, "Please correct the errors below.")
        return render(req, "adresse.html", {'form': form})

from product.models import order
def adress(req):
    add = userADRESS.objects.filter(user=req.user)
    orders = order.objects.filter(user=req.user)
    total = sum(order.amount * order.quantiti for order in orders)

    return render(req, "adresse.html", {'add': add, "orders": orders, "tot": total})

class UpdateAddress(View):
    def get(self, req, pk):
        add = get_object_or_404(userADRESS, id=pk)
        form = Profile(instance=add)
        return render(req, "update.html", {'form': form})

    def post(self, req, pk):
        add = get_object_or_404(userADRESS, id=pk)
        form = Profile(req.POST, instance=add)
        if form.is_valid():
            form.save()
            messages.success(req, "Address updated successfully.")
            return redirect("adress")
        else:
            messages.warning(req, "Please correct the errors below.")
        return render(req, "update.html", {'form': form})

def done(req):
    return render(req, "changepassword.html")

def active_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'The confirmation link was invalid, possibly because it has already been used.')
        return redirect('login')

from .form import PRFM

class EDI(View):
    def get(self, req):
        add = req.user
        form = PRFM(instance=add)
        return render(req, "editpro.html", {'form': form})

    def post(self, req):
        add = req.user
        form = PRFM(req.POST, req.FILES, instance=add)

        if form.is_valid():
            ins = form.save(commit=False)
            add.username = ins.username
            add.age = ins.age
            ins.save()
            add.save()

            return redirect('profile')
        else:
            return render(req, "editpro.html", {'form': form})
