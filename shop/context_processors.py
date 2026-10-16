from .models import Category

def categories_processor(request):
    """Делает список категорий доступным во всех шаблонах сайта"""
    return {
        'all_categories': Category.objects.all()
    }