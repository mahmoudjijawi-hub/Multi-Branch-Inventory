from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Branch, BranchInventory, Category, Product, StockTransfer, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'manager', 'created_at']
    search_fields = ['name', 'location']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'barcode', 'unit', 'price', 'category', 'min_quantity']
    list_filter = ['category', 'unit']
    search_fields = ['name', 'barcode']


@admin.register(BranchInventory)
class BranchInventoryAdmin(admin.ModelAdmin):
    list_display = ['branch', 'product', 'quantity']
    list_filter = ['branch', 'product__category']


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ['from_branch', 'to_branch', 'product', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'from_branch', 'to_branch']
