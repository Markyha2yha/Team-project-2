from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('account_info/', views.account_info, name='account_info'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
]