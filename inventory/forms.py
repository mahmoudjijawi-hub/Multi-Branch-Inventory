from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Branch, BranchInventory, Category, Product, StockTransfer


class LoginForm(AuthenticationForm):
  username = forms.CharField(
      label='اسم المستخدم',
      widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المستخدم'}),
  )
  password = forms.CharField(
      label='كلمة المرور',
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور'}),
  )


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'location', 'manager']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'اسم الفرع',
            'location': 'الموقع',
            'manager': 'المدير المسؤول',
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'barcode', 'unit', 'price', 'category', 'min_quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'min_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class BranchInventoryForm(forms.ModelForm):
    class Meta:
        model = BranchInventory
        fields = ['branch', 'product', 'quantity']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class StockTransferForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ['from_branch', 'to_branch', 'product', 'quantity', 'notes']
        widgets = {
            'from_branch': forms.Select(attrs={'class': 'form-control'}),
            'to_branch': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        from_branch = cleaned.get('from_branch')
        to_branch = cleaned.get('to_branch')
        product = cleaned.get('product')
        quantity = cleaned.get('quantity')

        if from_branch and to_branch and from_branch == to_branch:
            raise forms.ValidationError('لا يمكن التحويل لنفس الفرع.')

        if from_branch and product and quantity:
            inv = BranchInventory.objects.filter(branch=from_branch, product=product).first()
            if not inv or inv.quantity < quantity:
                raise forms.ValidationError('الكمية المتوفرة في الفرع المرسل غير كافية.')

        return cleaned


class InventorySearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='بحث',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ابحث بالاسم أو الباركود...'}),
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=False,
        label='الفرع',
        empty_label='جميع الفروع',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='التصنيف',
        empty_label='جميع التصنيفات',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
