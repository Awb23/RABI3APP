from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm , SetPasswordForm , PasswordResetForm
from django.contrib.auth.models import User
from .models import users, clien

class LoginForm(AuthenticationForm):
    class Meta:
        model = users
        fields = ['username', 'password']
        
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class NEW(UserCreationForm):
    class Meta:
        model = users
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

class RESETFORM(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}))

    class Meta:
        model = users
        fields = ('old_password', 'new_password1', 'new_password2')

class Profile(forms.ModelForm):
    class Meta:
        model = clien
        fields = ('firstname', 'lastname', 'phone', 'adress', 'country', 'city', 'state', 'zipcode')
        widgets = {
            'firstname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'adress': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip Code'}),
        }
        from django import forms
from .models import clien

class AddressForm(forms.ModelForm):
    class Meta:
        model = clien
        fields = ['country', 'phone', 'city', 'adress']  # Ensure 'adress' is the correct field name

    def clean(self):
        cleaned_data = super().clean()
        user = self.instance.user
       

        if clien.objects.filter(
            user=user,
           
        ).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('This address already exists for this user.')

class PASSERESETFORM(SetPasswordForm):
   pass
class mypasswordRESETFORM(PasswordResetForm):
   email=forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))