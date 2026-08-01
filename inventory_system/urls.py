from django.contrib import admin
from django.urls import include, path

from inventory.views import CustomLoginView, CustomLogoutView, healthz

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', healthz, name='healthz'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', include('inventory.urls')),
]
