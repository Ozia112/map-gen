"""
Test para verificar que las líneas punteadas se rendericen correctamente
"""
import sys
sys.path.insert(0, 'src')

import matplotlib
matplotlib.use('Agg')  # Sin GUI
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Crear figura 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Datos de prueba
X = np.arange(0, 10, 1)
Y = np.arange(0, 10, 1)
X_mesh, Y_mesh = np.meshgrid(X, Y)
Z_mesh = X_mesh + Y_mesh  # Plano simple

# Probar diferentes estilos de línea
print("Probando estilos de línea en contour 3D...")

try:
    # Línea sólida
    ax.contour(X_mesh, Y_mesh, Z_mesh, levels=[5], colors='red', 
               linewidths=2, linestyles=['solid'], zdir='z', offset=5)
    print("✅ linestyles=['solid'] funciona")
except Exception as e:
    print(f"❌ linestyles=['solid'] falló: {e}")

try:
    # Línea punteada
    ax.contour(X_mesh, Y_mesh, Z_mesh, levels=[10], colors='blue', 
               linewidths=2, linestyles=['dashed'], zdir='z', offset=10)
    print("✅ linestyles=['dashed'] funciona")
except Exception as e:
    print(f"❌ linestyles=['dashed'] falló: {e}")

try:
    # Guardar
    plt.savefig('test_linestyles.png', dpi=100)
    print("✅ Imagen guardada como test_linestyles.png")
    print("   Revisa la imagen para verificar visualmente")
except Exception as e:
    print(f"❌ Error al guardar: {e}")
