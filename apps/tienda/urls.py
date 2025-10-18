# app/tienda/urls.py
from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),\
    path('comprar/', views.comprar_producto, name='comprar_producto'),

]