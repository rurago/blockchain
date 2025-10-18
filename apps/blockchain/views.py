# apps/blockchain/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import BlockchainProducto, BlockchainOrden  # ✅ Nuevos nombres
from apps.tienda.models import Producto, Orden

# Inicialización del servicio blockchain
services = None
blockchain_status = "NOT_INITIALIZED"

try:
    from .services import BlockchainService
    services = BlockchainService()
    blockchain_status = "CONNECTED"
    print("🔗 Blockchain Service: CONECTADO a Ganache")
except Exception as e:
    blockchain_status = f"ERROR: {str(e)}"
    print(f"🔗 Blockchain Service: {blockchain_status}")
    
    # Servicio de emergencia
    class FallbackBlockchainService:
        def get_blockchain_info(self):
            return {
                'connected': False,
                'status': blockchain_status,
                'message': 'Ganache no disponible - Usando modo fallback'
            }
        def get_accounts(self): return []
        def send_test_transaction(self): return {'success': False, 'error': 'Modo fallback'}
    
    services = FallbackBlockchainService()

@csrf_exempt
def blockchain_info(request):
    """Información de la blockchain"""
    info = services.get_blockchain_info()
    return JsonResponse(info)

@csrf_exempt
def blockchain_accounts(request):
    """Cuentas de Ganache"""
    accounts = services.get_accounts()
    return JsonResponse({'accounts': accounts})

@csrf_exempt
def test_transaction(request):
    """Probar transacciones"""
    if request.method == 'POST':
        result = services.send_test_transaction()
        return JsonResponse(result)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def lista_productos(request):
    try:
        productos = BlockchainProducto.objects.all()
        
        if productos.exists():
            data = []
            for producto in productos:
                data.append({
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'precio': str(producto.precio),
                    'stock': producto.stock,
                    'vendedor': producto.vendedor.username,
                    'blockchain_tx': producto.blockchain_tx_hash,
                    'on_blockchain': bool(producto.blockchain_tx_hash)
                })
            return JsonResponse(data, safe=False)
        else:
            # Crear productos de prueba
            usuario, _ = User.objects.get_or_create(username='vendedor1')
            
            productos_ejemplo = [
                {"nombre": "Laptop Gaming Pro", "precio": 1.5, "stock": 5},
                {"nombre": "NFT Art Collection", "precio": 0.1, "stock": 100},
                {"nombre": "Smart Contract Service", "precio": 0.05, "stock": 50},
            ]
            
            for prod in productos_ejemplo:
                producto = Producto.objects.create(
                    nombre=prod["nombre"],
                    precio=prod["precio"],
                    stock=prod["stock"],
                    vendedor=usuario
                )
                # Registrar en blockchain
                tx_hash = services.create_product_on_blockchain(prod["nombre"], float(prod["precio"]))
                producto.blockchain_tx_hash = tx_hash
                producto.save()
            
            # Devolver productos
            productos = BlockchainProducto.objects.all()
            data = []
            for producto in productos:
                data.append({
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'precio': str(producto.precio),
                    'stock': producto.stock,
                    'vendedor': producto.vendedor.username,
                    'blockchain_tx': producto.blockchain_tx_hash,
                    'on_blockchain': bool(producto.blockchain_tx_hash)
                })
            return JsonResponse(data, safe=False)
            
    except Exception as e:
        return JsonResponse({'error': f'Error cargando productos: {str(e)}'}, status=500)

@csrf_exempt
@csrf_exempt
def crear_producto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            usuario, _ = User.objects.get_or_create(username='vendedor1')
            
            # Validar datos
            if not data.get('nombre') or not data.get('precio'):
                return JsonResponse({'error': 'Nombre y precio son requeridos'}, status=400)
            
            producto = Producto.objects.create(
                nombre=data.get('nombre', 'Producto Demo'),
                precio=data.get('precio', 100.00),
                stock=data.get('stock', 10),
                vendedor=usuario
            )
            
            # Registrar en blockchain solo si se solicita
            register_blockchain = data.get('register_blockchain', True)
            tx_hash = None
            if register_blockchain:
                tx_hash = services.create_product_on_blockchain(
                    producto.nombre, 
                    float(producto.precio)
                )
                producto.blockchain_tx_hash = tx_hash
                producto.save()
            
            return JsonResponse({
                'mensaje': 'Producto creado exitosamente' + (' en blockchain' if register_blockchain else ''),
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'precio': str(producto.precio),
                    'stock': producto.stock,
                    'blockchain_tx': tx_hash,
                    'on_blockchain': bool(tx_hash)
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)
    
@csrf_exempt
def comprar_producto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto_id = data.get('producto_id')
            cantidad = data.get('cantidad', 1)
            
            producto = BlockchainProducto.objects.get(id=producto_id)
            comprador, _ = User.objects.get_or_create(username='comprador1')
            
            if producto.stock < cantidad:
                return JsonResponse({'error': 'Stock insuficiente'}, status=400)
            
            total = producto.precio * cantidad
            
            orden = BlockchainProducto.objects.create(
                producto=producto,
                comprador=comprador,
                cantidad=cantidad,
                total_pagado=total
            )
            
            # Registrar compra en blockchain
            tx_hash = services.purchase_product_on_blockchain(
                producto_id, 
                cantidad, 
                float(total)
            )
            orden.blockchain_tx_hash = tx_hash
            orden.save()
            
            producto.stock -= cantidad
            producto.save()
            
            return JsonResponse({
                'mensaje': 'Compra realizada exitosamente en blockchain',
                'orden': {
                    'id': orden.id,
                    'producto': producto.nombre,
                    'cantidad': cantidad,
                    'total': str(total),
                    'blockchain_tx': tx_hash
                }
            })
            
        except BlockchainProducto.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
@csrf_exempt
def dashboard_completo(request):
    """Dashboard simplificado y robusto"""
    try:
        # Productos
        productos = BlockchainProducto.objects.all()
        productos_data = [{
            'id': p.id,
            'nombre': p.nombre,
            'precio': str(p.precio),
            'stock': p.stock,
            'vendedor': p.vendedor.username,
            'blockchain_tx': p.blockchain_tx_hash,
            'on_blockchain': bool(p.blockchain_tx_hash)
        } for p in productos]

        # Órdenes
        todas_ordenes = BlockchainOrden.objects.all()
        ordenes_recientes = todas_ordenes.order_by('-fecha_compra')[:10]
        ordenes_data = [{
            'id': o.id,
            'producto_nombre': o.producto.nombre,
            'comprador': o.comprador.username,
            'cantidad': o.cantidad,
            'total': str(o.total_pagado),
            'fecha_compra': o.fecha_compra.strftime("%Y-%m-%d %H:%M"),
            'blockchain_tx': o.blockchain_tx_hash,
            'on_blockchain': bool(o.blockchain_tx_hash)
        } for o in ordenes_recientes]

        # Blockchain info
        blockchain_info = services.get_blockchain_info()

        # Estadísticas
        stats = {
            'total_productos': productos.count(),
            'total_ordenes': todas_ordenes.count(),
            'productos_blockchain': productos.filter(blockchain_tx_hash__isnull=False).count(),
            'ordenes_blockchain': todas_ordenes.filter(blockchain_tx_hash__isnull=False).count(),
            'total_ventas': sum(float(o.total_pagado) for o in todas_ordenes),
            'transacciones_totales': blockchain_info.get('transaction_count', 0)
        }

        return JsonResponse({
            'estadisticas': stats,
            'productos': productos_data,
            'ordenes_recientes': ordenes_data,
            'blockchain_info': blockchain_info
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error en dashboard: {str(e)}'}, status=500)

@csrf_exempt
def transacciones_detalladas(request):
    """Obtener transacciones blockchain detalladas"""
    try:
        # Obtener últimas transacciones de la blockchain
        latest_block = services.w3.eth.get_block('latest')
        block_number = latest_block['number']
        
        transacciones_detalladas = []
        
        # Revisar últimos 5 bloques para transacciones
        for i in range(min(5, block_number + 1)):
            try:
                block = services.w3.eth.get_block(block_number - i)
                for tx_hash in block['transactions']:
                    tx = services.w3.eth.get_transaction(tx_hash)
                    tx_receipt = services.w3.eth.get_transaction_receipt(tx_hash)
                    
                    transacciones_detalladas.append({
                        'block_number': block['number'],
                        'hash': tx_hash.hex(),
                        'from': tx['from'],
                        'to': tx['to'] if tx['to'] else 'Contract Creation',
                        'value_eth': float(services.w3.from_wei(tx['value'], 'ether')),
                        'gas_used': tx_receipt['gasUsed'] if tx_receipt else 0,
                        'gas_price_gwei': float(services.w3.from_wei(tx['gasPrice'], 'gwei')),
                        'status': 'Success' if tx_receipt and tx_receipt['status'] == 1 else 'Failed',
                        'timestamp': block['timestamp'] if 'timestamp' in block else None
                    })
                    
                    # Máximo 20 transacciones
                    if len(transacciones_detalladas) >= 20:
                        break
                        
            except Exception as e:
                print(f"Error obteniendo bloque {block_number - i}: {e}")
                continue
                
        return JsonResponse({
            'total_transacciones': len(transacciones_detalladas),
            'transacciones': transacciones_detalladas
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

