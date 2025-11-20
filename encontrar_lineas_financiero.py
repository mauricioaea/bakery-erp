# encontrar_lineas_financiero.py
import re

def encontrar_consultas_financieras():
    print("🔍 BUSCANDO CONSULTAS FINANCIERAS VULNERABLES")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            lineas = file.readlines()
        
        consultas_vulnerables = []
        
        for num_linea, linea in enumerate(lineas, 1):
            # Buscar consultas en módulo financiero que no tengan panaderia_id
            if any(palabra in linea for palabra in ['Proveedor.query', 'RegistroDiario.query', 'PagoIndividual.query']):
                if 'panaderia_id' not in linea:
                    consultas_vulnerables.append((num_linea, linea.strip()))
        
        if consultas_vulnerables:
            print("🚨 CONSULTAS VULNERABLES ENCONTRADAS:")
            print("-" * 40)
            for num_linea, linea in consultas_vulnerables:
                print(f"Línea {num_linea}: {linea}")
                
            print(f"\n📋 TOTAL: {len(consultas_vulnerables)} consultas vulnerables")
        else:
            print("✅ No se encontraron consultas vulnerables")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_funcion_control_diario():
    print("\n🔍 BUSCANDO FUNCIÓN control_diario()")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Buscar la función control_diario
        patron = r'def control_diario\(\):(.*?)(?=def\s+\w+\(|\Z)'
        match = re.search(patron, contenido, re.DOTALL)
        
        if match:
            codigo_funcion = match.group(0)
            lineas = codigo_funcion.split('\n')
            
            print("📝 Código de control_diario() (primeras 30 líneas):")
            for i, linea in enumerate(lineas[:30]):
                print(f"{i+1:3}: {linea}")
        else:
            print("❌ No se encontró la función control_diario()")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    encontrar_consultas_financieras()
    mostrar_funcion_control_diario()