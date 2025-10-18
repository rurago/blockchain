# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from apps.blockchain.views import dashboard_completo  # ← Importar la vista real

def api_root(request):
    """Endpoint raíz de la API en JSON"""
    return JsonResponse({
        'message': '🚀 API de Tienda Blockchain - ¡Funcionando!',
        'version': '1.0.0',
        'endpoints': {
            'productos': '/api/productos/',
            'crear_producto': '/api/productos/crear/',
            'comprar': '/api/comprar/',
            'admin': '/admin/',
            'dashboard': '/dashboard/',
            'blockchain': '/api/blockchain/',
            'dashboard_api': '/api/dashboard/',

        },
        'frontend': 'Visita / para la aplicación React'
    })

urlpatterns = [
    # Admin y Frontend
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html')),
    
    # Dashboard - en la ruta correcta
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard_html'),
    
    # APIs
    path('api/blockchain/', include('apps.blockchain.urls')),
    path('api/', include('apps.tienda.urls')),
    path('api/dashboard/', dashboard_completo, name='dashboard_api'),
    
    # API Root
    path('api/', api_root),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)