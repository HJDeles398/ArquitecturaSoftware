from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app_practica4_bd/', include('app_practica4_bd.urls')), 
]
