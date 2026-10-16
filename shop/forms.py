from django import forms
from .models import Product, Category

class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'old_price', 'stock', 'description', 'main_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Сухой корм для кошек Royal Canin'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'old_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00 (необязательно)', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Количество на складе'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание состава и веса корма'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
        }