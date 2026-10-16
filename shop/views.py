from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Product, Category
from .forms import ProductCreateForm


def shop_catalog(request, category_slug=None):
    selected_category = None
    products_qs = Product.objects.filter(is_active=True).select_related('category').order_by('-created_at')

    cat_slug = category_slug or request.GET.get('category')
    if cat_slug:
        selected_category = get_object_or_404(Category, slug=cat_slug)
        products_qs = products_qs.filter(category=selected_category)

    search_query = request.GET.get('search', '').strip()
    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Пагинация: 12 товаров на страницу (сетка 4x3)
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
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
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