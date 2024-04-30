
from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
 
    path("register/", views.registerPage, name="register"),
   path('verify/<str:identifier>/', views.verify_otp, name='verifyotp'),
    path("login/", views.loginPage, name="login"),
    path("", views.homePage, name="home"),
    path('logout/', views.logoutPage, name='logout'),

]
