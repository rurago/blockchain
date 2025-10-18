#!/usr/bin/env python
"""
Punto de entrada principal para Mi Tienda Blockchain
"""
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    
    from django.core.management import execute_from_command_line
    
    # Si no hay argumentos, mostrar ayuda
    if len(sys.argv) == 1:
        print("Mi Tienda Blockchain")
        print("Usar: python app.py [comando]")
        print("Comandos disponibles: runserver, migrate, createsuperuser, shell")
        sys.exit(1)
    
    # Mapear comandos simples
    if sys.argv[1] == "runserver":
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
    elif sys.argv[1] == "migrate":
        execute_from_command_line(['manage.py', 'migrate'])
    elif sys.argv[1] == "createsuperuser":
        execute_from_command_line(['manage.py', 'createsuperuser'])
    elif sys.argv[1] == "shell":
        execute_from_command_line(['manage.py', 'shell'])
    else:
        execute_from_command_line(['manage.py'] + sys.argv[1:])