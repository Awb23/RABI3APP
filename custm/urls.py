from django.urls import path
from custm import views 
from .form import LoginForm , RESETFORM , mypasswordRESETFORM , PASSERESETFORM


from django.contrib.auth import views as authv
urlpatterns = [
   


    path('active_account/<uidb64>/<token>', views.active_account , name = 'verify_email'),


path("accounts/sign up/",views.Sign.as_view(),name="sign" ),
path("loug out",views.loug,name="logout" ),
path("accounts/login/",authv.LoginView.as_view(template_name="login.html",authentication_form=LoginForm),name="login" ),
path("Password-changed/",authv.PasswordChangeView.as_view(template_name="pas/reset.html",form_class=RESETFORM , success_url='/Passwordchanged'),name="reset" ),
path("",views.home,name="home" ),
path("adress",views.adress,name="adress" ),
path("profile",views.PROFILE.as_view(),name="profile" ),
path("Passwordchanged",views.done,name="done" ),

path("updateadrsse/<int:pk>",views.UpdateAddress.as_view(),name="adru" ),
path("Password-reset/",authv.PasswordResetView.as_view(template_name="pas/Password-reset.html",form_class=mypasswordRESETFORM),name="Password-reset" ),


path("Password-reset_done/",authv.PasswordResetDoneView.as_view(template_name="pas/Password-reset_done.html"),name="password_reset_done" ),


path("Password-reset_conferme/<uidb64>/<token>",authv.PasswordResetConfirmView.as_view(template_name="pas/respaswd.html",form_class=PASSERESETFORM),name="password_reset_confirm" ),

path("Password-reset_complete/",authv.PasswordResetCompleteView.as_view(template_name="pas/Password-reset_complete.html" ),name="password_reset_complete" ),



   

   
   
    
  
  
]

