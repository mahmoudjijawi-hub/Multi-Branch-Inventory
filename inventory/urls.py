from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Branches
    path('branches/', views.branch_list, name='branch_list'),
    path('branches/create/', views.branch_create, name='branch_create'),
    path('branches/<int:pk>/edit/', views.branch_edit, name='branch_edit'),
    path('branches/<int:pk>/delete/', views.branch_delete, name='branch_delete'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/create/', views.inventory_create, name='inventory_create'),
    path('inventory/<int:pk>/edit/', views.inventory_edit, name='inventory_edit'),

    # Transfers
    path('transfers/', views.transfer_list, name='transfer_list'),
    path('transfers/create/', views.transfer_create, name='transfer_create'),
    path('transfers/<int:pk>/approve/', views.transfer_approve, name='transfer_approve'),
    path('transfers/<int:pk>/reject/', views.transfer_reject, name='transfer_reject'),

    # Reports
    path('reports/', views.branch_report, name='branch_report'),
]
