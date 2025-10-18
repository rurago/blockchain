# apps/blockchain/models.py
from django.db import models
from django.contrib.auth.models import User

class BlockchainProducto(models.Model):
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=10)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    blockchain_tx_hash = models.CharField(max_length=100, blank=True, null=True)  # ¡ESTE CAMPO!
    blockchain_product_id = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class BlockchainOrden(models.Model):
    producto = models.ForeignKey(BlockchainProducto, on_delete=models.CASCADE)
    comprador = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    blockchain_tx_hash = models.CharField(max_length=100, blank=True, null=True)  # ¡Y ESTE!
    
    def __str__(self):
        return f"Orden #{self.id}"