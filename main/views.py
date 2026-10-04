from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'main/home.html')

def about(request):
    return render(request, 'main/about.html')

def contacts(request):
    return render(request, 'main/home.html')

def account_info(request):
    return render(request, 'main/account_info.html')

def login_view(request):
   return render(request, 'main/login.html')

def register_view(request):
   return render(request, 'main/register.html')

def contact_view(request):
   return render(request, 'main/contact.html')

