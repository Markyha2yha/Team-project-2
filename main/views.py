from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shop.models import Profile
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm


def home(request):
    return render(request, 'main/home.html')

def about(request):
    return render(request, 'main/about.html')

def contacts(request):
    return render(request, 'main/home.html')

def contact_view(request):
    return render(request, 'main/contact.html')


# Вход в аккаунт
def login_view(request):
    if request.user.is_authenticated:
        return redirect('account_info')

    if request.method == 'POST':
        email_or_username = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Проверяем вход как по username, так и по email
        user = authenticate(request, username=email_or_username, password=password)
        if not user:
            from django.contrib.auth.models import User
            try:
                user_obj = User.objects.get(email=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect('account_info')
        else:
            messages.error(request, 'Неверный email/логин или пароль.')

    return render(request, 'main/login.html')


# Регистрация
def register_view(request):
    if request.user.is_authenticated:
        return redirect('account_info')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Создаем связанный профиль
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('account_info')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegisterForm()

    return render(request, 'main/register.html', {'form': form})


# Выход из аккаунта
def logout_view(request):
    logout(request)
    return redirect('home')


# Личный кабинет (только для авторизованных)
@login_required
def account_info(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('account_info')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    return render(request, 'main/account_info.html', {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
    })

