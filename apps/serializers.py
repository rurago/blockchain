from rest_framework import serializers
from .models import Producto, Orden

class ProductoSerializer(serializers.ModelSerializer):
    vendedor_nombre = serializers.CharField(source='vendedor.username', read_only=True)
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'stock', 
                 'vendedor', 'vendedor_nombre', 'estado', 'fecha_creacion']

class OrdenSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    comprador_nombre = serializers.CharField(source='comprador.username', read_only=True)
    
    class Meta:
        model = Orden
        fields = ['id', 'producto', 'producto_nombre', 'comprador', 'comprador_nombre',
                 'cantidad', 'total_pagado', 'estado', 'fecha_compra', 'transaccion_hash']