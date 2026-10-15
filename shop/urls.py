from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop_catalog, name='catalog'),
    path('category/<slug:category_slug>/', views.shop_catalog, name='catalog_by_category'),
    path('add/', views.add_product, name='add_product'),
    path('category/add/new/', views.add_category, name='add_category'),  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
]