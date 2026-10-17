from django import forms
from .models import Product, Category

class ProductCreateForm(forms.ModelForm):
    available_tastes = forms.CharField(label='Варианты вкуса (через запятую)', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Курица и рис, Говядина, Лосось'}))
    available_packagings = forms.CharField(label='Варианты фасовки (через запятую)', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '400 г, 1.5 кг, 3 кг'}))

    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'old_price', 'stock', 'description', 'available_tastes', 'available_packagings', 'main_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Сухой корм для кошек Royal Canin'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'old_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00 (необязательно)', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Количество на складе'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание состава и веса корма'}),
            'available_tastes': forms.TextInput(attrs={'class': 'form-control'}),
            'available_packagings': forms.TextInput(attrs={'class': 'form-control'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
        }