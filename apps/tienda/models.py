# apps/tienda/models.py
from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('agotado', 'Agotado')
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

class Orden(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada')
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    comprador = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_compra = models.DateTimeField(auto_now_add=True)
    transaccion_hash = models.CharField(max_length=100, blank=True)  # Para blockchain
    
    def __str__(self):
        return f"Orden #{self.id} - {self.producto.nombre}"