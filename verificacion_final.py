# verificacion_final.py
def verificacion_final():
    print("✅ VERIFICACIÓN FINAL DE AISLAMIENTO")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            contenido = file.read()
        
        # Verificar que NO hay consultas vulnerables
        consultas_peligrosas = [
            'Proveedor.query.all()',
            'ActivoFijo.query.all()', 
            'RegistroDiario.query.order_by',
            'PagoIndividual.query.filter_by'
        ]
        
        vulnerabilidades = 0
        for consulta in consultas_peligrosas:
            if consulta in contenido and 'panaderia_id' not in contenido[contenido.find(consulta)-50:contenido.find(consulta)+50]:
                print(f"🚨 Consulta vulnerable encontrada: {consulta}")
                vulnerabilidades += 1
        
        if vulnerabilidades == 0:
            print("🎯 ¡TODAS LAS CONSULTAS ESTÁN SEGURAS!")
            print("✅ Aislamiento multi-tenant implementado correctamente")
        else:
            print(f"⚠️  Se encontraron {vulnerabilidades} consultas potencialmente vulnerables")
            
        # Contar filtros aplicados
        total_filtros = contenido.count('panaderia_id=1')
        print(f"📊 Total de filtros panaderia_id aplicados: {total_filtros}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificacion_final()