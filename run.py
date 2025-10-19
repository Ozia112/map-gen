"""
Launcher script para VISTAR Map Generator
Ejecuta la aplicación con las rutas correctas configuradas
Incluye funcionalidad de reinicio automático si hay procesos previos
"""
import sys
import os
import subprocess
import time
import socket

def is_port_in_use(port, host='0.0.0.0'):
    """Verifica si un puerto está en uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True

def check_and_kill_processes():
    """Verifica y cierra procesos Python existentes si hay alguno usando el puerto"""
    # Verificar si el puerto 8080 está en uso
    if not is_port_in_use(8080):
        print("Puerto 8080 libre. No hay procesos previos.")
        return
    
    print("Puerto 8080 en uso. Intentando cerrar procesos Python...")
    
    try:
        # Intentar cerrar procesos Python que puedan estar usando el puerto
        # En Windows, usamos netstat para encontrar el proceso
        result = subprocess.run(
            ["powershell", "-Command", 
             "Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid_str in pids:
                try:
                    pid = int(pid_str.strip())
                    subprocess.run(
                        ["powershell", "-Command", f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
                        timeout=2
                    )
                    print(f"Proceso {pid} cerrado.")
                except (ValueError, subprocess.TimeoutExpired):
                    pass
            
            time.sleep(2)
            print("Procesos cerrados.")
        else:
            print("No se encontraron procesos en el puerto.")
    except Exception as e:
        print(f"Advertencia al verificar procesos: {e}")
        # Continuar de todas formas

# Agregar el directorio src al path de Python
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_dir)

# Importar y ejecutar main
from main import main

if __name__ == '__main__':
    # Verificar y cerrar procesos previos si los hay
    check_and_kill_processes()
    
    # Ejecutar la aplicación
    print("Iniciando VISTAR Map Generator...")
    main()
