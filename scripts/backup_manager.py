# scripts/backup_manager.py - VERSIÓN COMPLETA ACTUALIZADA
import os
import datetime
import zipfile
from pathlib import Path

def crear_backup(tipo="manual", descripcion=""):
    """Crear backup completo con todos los módulos"""
    
    # Directorios
    backups_dir = Path("backups")
    automaticos_dir = backups_dir / "automaticos"
    manuales_dir = backups_dir / "manuales"
    emergencia_dir = backups_dir / "emergencia"
    
    # Asegurar que existen los directorios
    automaticos_dir.mkdir(parents=True, exist_ok=True)
    manuales_dir.mkdir(parents=True, exist_ok=True)
    emergencia_dir.mkdir(parents=True, exist_ok=True)
    
    # Timestamp para el nombre
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Definir ubicación según tipo
    if tipo == "automatico":
        carpeta_destino = automaticos_dir
        nombre_archivo = f"auto_{timestamp}.zip"
    elif tipo == "emergencia":
        carpeta_destino = emergencia_dir
        nombre_archivo = f"emergencia_{timestamp}.zip"
    else:
        carpeta_destino = manuales_dir
        if descripcion:
            nombre_limpio = descripcion.replace(" ", "_")[:20]
            nombre_archivo = f"manual_{timestamp}_{nombre_limpio}.zip"
        else:
            nombre_archivo = f"manual_{timestamp}.zip"
    
    archivo_backup = carpeta_destino / nombre_archivo
    
    # Archivos y directorios importantes a respaldar
    elementos_importantes = [
        "app.py",
        "models.py", 
        "reportes.py",
        "requirements.txt",
        "crear_super_admin.py",
        "inicializar_bd.py",
        "multicliente_middleware.py",
        "templates/",
        "utilidades/",
        "facturacion/", 
        "static/"
    ]
    
    try:
        with zipfile.ZipFile(archivo_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Procesar cada elemento
            for elemento in elementos_importantes:
                elemento_path = Path(elemento)
                
                if elemento.endswith('/'):  # Es un directorio
                    directorio = elemento.rstrip('/')
                    if os.path.exists(directorio):
                        for root, dirs, files in os.walk(directorio):
                            for file in files:
                                ruta_completa = os.path.join(root, file)
                                nombre_en_zip = ruta_completa
                                zipf.write(ruta_completa, nombre_en_zip)
                                print(f"✅ Agregado: {ruta_completa}")
                else:  # Es un archivo
                    if os.path.exists(elemento):
                        zipf.write(elemento, elemento)
                        print(f"✅ Agregado: {elemento}")
        
        tamaño_mb = os.path.getsize(archivo_backup) / (1024 * 1024)
        
        print("=" * 50)
        print("🎉 BACKUP COMPLETO CREADO EXITOSAMENTE")
        print("=" * 50)
        print(f"📁 Archivo: {nombre_archivo}")
        print(f"📍 Ubicación: {archivo_backup}")
        print(f"📊 Tamaño: {tamaño_mb:.2f} MB")
        print(f"🎯 Tipo: {tipo}")
        if descripcion:
            print(f"📝 Descripción: {descripcion}")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR creando backup: {e}")
        return False

def listar_backups():
    """Listar backups disponibles"""
    backups_dir = Path("backups")
    
    if not backups_dir.exists():
        print("❌ No existe el directorio de backups")
        return
    
    print("=" * 60)
    print("📋 BACKUPS DISPONIBLES")
    print("=" * 60)
    
    total = 0
    for tipo in ["automaticos", "manuales", "emergencia"]:
        carpeta_tipo = backups_dir / tipo
        if carpeta_tipo.exists():
            archivos_zip = list(carpeta_tipo.glob("*.zip"))
            for archivo in sorted(archivos_zip, key=os.path.getmtime, reverse=True)[:10]:
                tamaño_mb = os.path.getsize(archivo) / (1024 * 1024)
                fecha = datetime.datetime.fromtimestamp(os.path.getmtime(archivo))
                print(f"  {tipo:12} {archivo.name:40} {tamaño_mb:5.1f} MB")
                total += 1
    
    print(f"\n📊 Total backups: {total}")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "create":
            tipo = sys.argv[2] if len(sys.argv) > 2 else "manual"
            descripcion = sys.argv[3] if len(sys.argv) > 3 else ""
            crear_backup(tipo, descripcion)
        
        elif comando == "list":
            listar_backups()
        
        else:
            print("Uso: python backup_manager.py [create|list]")
            print("  create [tipo] [descripcion] - Crear backup")
            print("  list - Listar backups disponibles")
    else:
        print("Sistema de Backup - Panadería ERP")
        print("Uso: python backup_manager.py [create|list]")