import os
import glob

def limpieza_total():
    print("🧹 LIMPIEZA TOTAL DEL SISTEMA")
    
    # Eliminar todas las bases de datos
    archivos_db = glob.glob("*.db") + glob.glob("*.sqlite") + glob.glob("*.sqlite3")
    
    for archivo in archivos_db:
        try:
            os.remove(archivo)
            print(f"✅ Eliminado: {archivo}")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar {archivo}: {e}")
    
    print("🎉 ¡Limpieza completada!")
    print("💡 Ahora ejecuta 'python app.py' para crear una base de datos nueva y limpia")

if __name__ == '__main__':
    limpieza_total()