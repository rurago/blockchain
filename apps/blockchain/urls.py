# apps/blockchain/urls.py
from django.urls import path
from . import views

app_name = 'blockchain'

urlpatterns = [
    # Información de blockchain
    path('', views.blockchain_info, name='blockchain_info'),
    path('accounts/', views.blockchain_accounts, name='blockchain_accounts'),
    path('test-transaction/', views.test_transaction, name='test_transaction'),
    
    # Productos de blockchain (diferentes de los de tienda)
    path('blockchain-products/', views.lista_productos, name='lista_productos_blockchain'),
    path('blockchain-products/create/', views.crear_producto, name='crear_producto_blockchain'),
    path('blockchain-products/buy/', views.comprar_producto, name='comprar_producto_blockchain'),
    
    # Dashboard y transacciones
    path('dashboard/', views.dashboard_completo, name='dashboard_completo'),
    path('transactions-detailed/', views.transacciones_detalladas, name='transacciones_detalladas'),

]