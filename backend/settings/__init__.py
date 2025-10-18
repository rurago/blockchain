from .base import *

# Determinar qué configuración usar
try:
    from .development import *
    print("✅ Usando configuración de desarrollo")
except ImportError as e:
    try:
        from .production import *
        print("✅ Usando configuración de producción")
    except ImportError:
        print("⚠️  No se encontró configuración específica, usando base")