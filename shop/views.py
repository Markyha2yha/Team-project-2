from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Product, Category, Favorite
from .forms import ProductCreateForm
from decimal import Decimal
from .models import Cart, CartItem


def shop_catalog(request, category_slug=None):
    selected_category = None
    products_qs = Product.objects.filter(is_active=True).select_related('category').order_by('-created_at')

    cat_slug = category_slug or request.GET.get('category')
    if cat_slug:
        # Ищем категорию по слагу или названию
        selected_category = Category.objects.filter(
            Q(slug__iexact=cat_slug) | Q(name__icontains=cat_slug)
        ).first()
        if selected_category:
            products_qs = products_qs.filter(category=selected_category)
        else:
            # Если точной категории нет, ищем товары по названию/описанию
            products_qs = products_qs.filter(
                Q(name__icontains=cat_slug) | Q(description__icontains=cat_slug)
            )

    search_query = request.GET.get('search', '').strip()
    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    paginator = Paginator(products_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'shop/catalog.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
    })

def product_detail(request, product_id):
    """Детальная страница товара по Примеру 2"""
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, product=product).exists()
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'is_favorite': is_favorite,
    })


def add_product(request):
    if not Category.objects.exists():
        default_cats = ['Cat (Кошки)', 'Dog (Собаки)', 'Parrot (Попугаи)', 'Fish (Рыбки)', 'Rabbit (Кролики)',
                        'Horse (Лошади)']
        for name in default_cats:
            Category.objects.create(name=name)

    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Корм "{product.name}" успешно добавлен в магазин!')
            return redirect('shop:catalog')
    else:
        form = ProductCreateForm()

    return render(request, 'shop/add_product.html', {'form': form})


def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            cat, created = Category.objects.get_or_create(name=name)
            if created:
                messages.success(request, f'Категория "{name}" успешно создана!')
            else:
                messages.info(request, f'Категория "{name}" уже существовала.')
    return redirect('shop:add_product')


@require_POST
def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        qty = int(request.POST.get('quantity', 1))
    except ValueError:
        qty = 1

    if product.stock >= qty and qty > 0:
        product.stock -= qty
        product.save()
        messages.success(request,
                         f'🎉 Вы успешно приобрели "{product.name}" ({qty} шт.)! На складе осталось: {product.stock} шт.')
    elif product.stock > 0:
        messages.error(request, f'Невозможно купить {qty} шт. Доступно только: {product.stock} шт.')
    else:
        messages.error(request, f'К сожалению, товар "{product.name}" закончился на складе!')

    return redirect(request.META.get('HTTP_REFERER', 'shop:catalog'))


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Корм "{product.name}" успешно обновлен!')
            return redirect('shop:catalog')
    else:
        form = ProductCreateForm(instance=product)

    return render(request, 'shop/edit_product.html', {'form': form, 'product': product})


@require_POST
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    product.delete()
    messages.success(request, f'Корм "{product_name}" успешно удален с площадки.')
    return redirect('shop:catalog')

def toggle_favorite(request, product_id):
    if request.method != 'POST':
        return redirect('shop:product_detail', product_id=product_id)
    if not request.user.is_authenticated:
        messages.info(request, 'Войдите в аккаунт, чтобы сохранять избранные товары.')
        return redirect('login')
    product = get_object_or_404(Product, id=product_id, is_active=True)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        favorite.delete()
        messages.info(request, f'«{product.name}» удалён из избранного.')
    else:
        messages.success(request, f'«{product.name}» добавлен в избранное.')
    return redirect(request.META.get('HTTP_REFERER', 'shop:product_detail') or 'shop:catalog')


def favorites_list(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Войдите в аккаунт, чтобы просматривать избранное.')
        return redirect('login')
    products = Product.objects.filter(favorited_by__user=request.user, is_active=True).select_related('category')
    return render(request, 'shop/favorites.html', {'products': products})


def _get_cart(request):
    """Возвращает или создает корзину для пользователя или анонимной сессии"""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Если до входа была сессионная корзина — объединяем товары
        if request.session.session_key:
            session_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if session_cart and session_cart != cart:
                for item in session_cart.items.all():
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart, product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    if not created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                session_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def cart_detail(request):
    """Страница корзины со списком товаров и Order Summary"""
    cart = _get_cart(request)
    cart_items = cart.items.select_related('product', 'product__category')

    subtotal = sum(item.subtotal() for item in cart_items)

    # Расчет доставки: бесплатно при заказе от $100 или пустой корзине, иначе $15
    shipping = Decimal('0.00') if (subtotal >= Decimal('100.00') or subtotal == 0) else Decimal('15.00')

    # Расчет налога (например, 5%)
    tax = (subtotal * Decimal('0.05')).quantize(Decimal('0.01')) if subtotal > 0 else Decimal('0.00')

    total = subtotal + shipping + tax

    return render(request, 'shop/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
    })


@require_POST
def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_cart(request)

    try:
        qty = int(request.POST.get('quantity', 1))
    except ValueError:
        qty = 1

    if qty < 1:
        qty = 1

    if product.stock < qty:
        messages.error(request, f'Недостаточно товара на складе. Доступно: {product.stock} шт.')
        return redirect(request.META.get('HTTP_REFERER', 'shop:catalog'))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': qty}
    )

    if not created:
        if cart_item.quantity + qty > product.stock:
            messages.error(request, f'Вы не можете добавить больше {product.stock} шт.')
            return redirect('shop:cart')
        cart_item.quantity += qty
        cart_item.save()

    messages.success(request, f'«{product.name}» добавлен в корзину!')
    return redirect('shop:cart')


@require_POST
def update_cart_item(request, item_id):
    """Изменение количества [+] или [-]"""
    cart = _get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    action = request.POST.get('action')

    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, f'Максимальный остаток на складе: {cart_item.product.stock} шт.')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, f'«{cart_item.product.name}» удален из корзины.')

    return redirect('shop:cart')


@require_POST
def remove_from_cart(request, item_id):
    """Удаление товара из корзины кнопкой крестика"""
    cart = _get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    name = cart_item.product.name
    cart_item.delete()
    messages.info(request, f'Товар «{name}» удален из корзины.')
    return redirect('shop:cart')


@require_POST
def checkout(request):
    """Оформление заказа"""
    cart = _get_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Ваша корзина пуста.')
        return redirect('shop:catalog')

    # Списываем остаток товара на складе
    for item in cart.items.all():
        if item.product.stock >= item.quantity:
            item.product.stock -= item.quantity
            item.product.save()

    # Очищаем корзину после успешной покупки
    cart.items.all().delete()
    messages.success(request, '🎉 Поздравляем! Ваш заказ успешно оформлен и передан в доставку.')
    return redirect('shop:cart')