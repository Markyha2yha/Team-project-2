from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop_catalog, name='catalog'),
    path('category/<slug:category_slug>/', views.shop_catalog, name='catalog_by_category'),
    path('add/', views.add_product, name='add_product'),
    path('category/add/new/', views.add_category, name='add_category'),

    # Новые маршруты
    path('buy/<int:product_id>/', views.buy_product, name='buy_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
]