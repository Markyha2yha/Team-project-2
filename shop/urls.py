from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop_catalog, name='catalog'),
    path('category/<slug:category_slug>/', views.shop_catalog, name='catalog_by_category'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # <-- НОВЫЙ МАРШРУТ
    path('add/', views.add_product, name='add_product'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('favorite/<int:product_id>/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('category/add/new/', views.add_category, name='add_category'),
    path('buy/<int:product_id>/', views.buy_product, name='buy_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
]