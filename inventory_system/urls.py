from django.contrib import admin
from django.urls import include, path

from inventory.views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', include('inventory.urls')),
]
