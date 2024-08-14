from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View

from product.models import prod
from custm.models import users, clien
from .form import NEW, LoginForm, Profile


def home(request):
    po = prod.objects.all()
    return render(request, "ap/index.html", {'po': po})


@login_required
def loug(request):
    logout(request)
    return redirect("home")


class Sign(View):
    def get(self, req):
        form = NEW()
        return render(req, "sign.html", {'form': form})

    def post(self, req):
        form = NEW(req.POST)
        if form.is_valid():
            form.save()
            messages.success(req, "You have successfully signed up.")
            return redirect("login")
        else:
            messages.warning(req, "Please correct the errors below.")
        return render(req, 'sign.html', {'form': form})


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
            j = clien(**clien_data)
            j.save()
            messages.success(req, "Profile updated successfully.")
            return redirect("adress")
        else:
            messages.warning(req, "Please correct the errors below.")
        return render(req, "adresse.html", {'form': form})


def adress(req):
    add = clien.objects.filter(user=req.user)
    return render(req, "adresse.html", {'add': add})


class UpdateAddress(View):
    def get(self, req, pk):
        add = get_object_or_404(clien, id=pk)
        form = Profile(instance=add)
        return render(req, "update.html", {'form': form})

    def post(self, req, pk):
        add = get_object_or_404(clien, id=pk)
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
