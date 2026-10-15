from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category
from .forms import ProductCreateForm


def shop_catalog(request, category_slug=None):
    selected_category = None
    products = Product.objects.filter(is_active=True).select_related('category')

    cat_slug = category_slug or request.GET.get('category')
    if cat_slug:
        selected_category = get_object_or_404(Category, slug=cat_slug)
        products = products.filter(category=selected_category)

    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    categories = Category.objects.all()

    return render(request, 'shop/catalog.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
    })


def add_product(request):
    """Страница добавления корма"""
    # Если база категорий пуста, автоматически создаем стандартный список животных
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
    """Быстрое добавление новой категории животного пользователем"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            cat, created = Category.objects.get_or_create(name=name)
            if created:
                messages.success(request, f'Категория "{name}" успешно создана!')
            else:
                messages.info(request, f'Категория "{name}" уже существовала.')
    return redirect('shop:add_product')