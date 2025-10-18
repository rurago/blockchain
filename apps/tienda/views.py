# apps/tienda/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
from .models import Producto, Orden

@csrf_exempt
def lista_productos(request):
    """Listar productos"""
    productos = Producto.objects.all()
    data = [{
        'id': p.id,
        'nombre': p.nombre,
        'precio': str(p.precio),
        'stock': p.stock,
        'vendedor': p.vendedor.username,
    } for p in productos]
    return JsonResponse(data, safe=False)

@csrf_exempt
def crear_producto(request):
    """Crear producto"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            usuario, _ = User.objects.get_or_create(username='vendedor1')
            
            producto = Producto.objects.create(
                nombre=data.get('nombre', 'Producto Demo'),
                precio=data.get('precio', 100.00),
                stock=data.get('stock', 10),
                vendedor=usuario
            )
            
            return JsonResponse({
                'mensaje': 'Producto creado exitosamente',
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'precio': str(producto.precio),
                    'stock': producto.stock,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def comprar_producto(request):
    """Comprar producto"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto_id = data.get('producto_id')
            cantidad = data.get('cantidad', 1)
            
            producto = Producto.objects.get(id=producto_id)
            comprador, _ = User.objects.get_or_create(username='comprador1')
            
            if producto.stock < cantidad:
                return JsonResponse({'error': 'Stock insuficiente'}, status=400)
            
            total = producto.precio * cantidad
            orden = Orden.objects.create(
                producto=producto,
                comprador=comprador,
                cantidad=cantidad,
                total_pagado=total
            )
            
            producto.stock -= cantidad
            producto.save()
            
            return JsonResponse({
                'mensaje': 'Compra realizada exitosamente',
                'orden': {
                    'id': orden.id,
                    'producto': producto.nombre,
                    'cantidad': cantidad,
                    'total': str(total),
                }
            })
        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)