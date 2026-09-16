#!/usr/bin/env python3
"""
Script de migración de SQLite a PostgreSQL
Para el sistema PanaderíaPro - VERSIÓN CORREGIDA
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging
from pathlib import Path

# Configurar logging (sin emojis para evitar problemas en Windows)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migracion.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MigradorSQLiteAPostgreSQL:
    def __init__(self):
        self.pg_config = {
            'host': 'localhost',
            'port': 5433,
            'database': 'panaderia_master',
            'user': 'postgres',
            'password': 'PanaderiaPro2026!'
        }
        self.pg_conn = None
        self.pg_cursor = None

    def conectar_postgresql(self):
        try:
            self.pg_conn = psycopg2.connect(**self.pg_config)
            self.pg_cursor = self.pg_conn.cursor()
            logger.info("Conexion a PostgreSQL exitosa (puerto 5433)")
            return True
        except Exception as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            return False

    def obtener_tablas_sqlite(self, db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
            AND name != 'alembic_version'
            ORDER BY name
        """)
        tablas = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tablas

    def obtener_esquema_tabla(self, db_file, tabla):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tabla})")
        columns = cursor.fetchall()
        conn.close()
        return columns

    def convertir_tipo_sqlite_a_postgres(self, tipo_sqlite, columna_nombre=None):
        tipo_upper = tipo_sqlite.upper()
        
        if 'INT' in tipo_upper:
            # Si la columna se llama 'activo', usar BOOLEAN
            if columna_nombre and columna_nombre.lower() == 'activo':
                return 'BOOLEAN'
            return 'INTEGER'
        elif 'REAL' in tipo_upper or 'FLOAT' in tipo_upper:
            return 'FLOAT'
        elif 'TEXT' in tipo_upper or 'VARCHAR' in tipo_upper:
            return 'TEXT'
        elif 'BLOB' in tipo_upper:
            return 'BYTEA'
        elif 'DATETIME' in tipo_upper or 'DATE' in tipo_upper:
            return 'TIMESTAMP'
        elif 'BOOL' in tipo_upper:
            return 'BOOLEAN'
        elif 'DECIMAL' in tipo_upper or 'NUMERIC' in tipo_upper:
            return 'DECIMAL(10,2)'
        else:
            return 'TEXT'

    def convertir_valor(self, valor, tipo_sqlite, columna_nombre=None):
        """Convertir valores de SQLite a PostgreSQL"""
        if valor is None:
            return None
        
        # Si es la columna 'activo', convertir a booleano
        if columna_nombre and columna_nombre.lower() == 'activo':
            if isinstance(valor, int):
                return bool(valor)
            if isinstance(valor, str):
                return valor.lower() in ('1', 'true', 'yes', 'si')
            return bool(valor)
        
        # Si es fecha, asegurar formato correcto
        if columna_nombre and 'fecha' in columna_nombre.lower():
            if isinstance(valor, str):
                try:
                    # Intentar convertir string a datetime
                    return datetime.strptime(valor, '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        return datetime.strptime(valor, '%Y-%m-%d')
                    except:
                        return valor
        
        return valor

    def crear_tabla_postgresql(self, tabla, columns, schema='public'):
        try:
            column_defs = []
            primary_key = None
            
            for col in columns:
                col_name = col[1]
                col_type = self.convertir_tipo_sqlite_a_postgres(col[2], col_name)
                col_notnull = 'NOT NULL' if col[3] == 1 else ''
                
                if col[5] == 1:
                    primary_key = col_name
                    if 'INTEGER' in col_type:
                        col_type = 'SERIAL'
                        col_notnull = 'NOT NULL'
                
                column_defs.append(f"{col_name} {col_type} {col_notnull}".strip())
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {schema}.{tabla} (\n  " + ",\n  ".join(column_defs)
            if primary_key:
                create_sql += f",\n  PRIMARY KEY ({primary_key})"
            create_sql += "\n);"
            
            self.pg_cursor.execute(create_sql)
            self.pg_conn.commit()
            logger.info(f"Tabla {schema}.{tabla} creada")
            return True
            
        except Exception as e:
            logger.error(f"Error creando tabla {tabla}: {e}")
            return False

    def migrar_datos_tabla(self, db_sqlite, tabla, schema='public'):
        try:
            sqlite_conn = sqlite3.connect(db_sqlite)
            sqlite_conn.row_factory = sqlite3.Row
            sqlite_cursor = sqlite_conn.cursor()
            
            sqlite_cursor.execute(f"SELECT * FROM {tabla}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                sqlite_conn.close()
                return
            
            columns = [description[0] for description in sqlite_cursor.description]
            
            # Obtener tipos de las columnas
            tipos = {col[1]: col[2] for col in self.obtener_esquema_tabla(db_sqlite, tabla)}
            
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)
            insert_sql = f"INSERT INTO {schema}.{tabla} ({column_names}) VALUES ({placeholders})"
            
            for row in rows:
                values = []
                for col in columns:
                    valor = row[col]
                    tipo_sqlite = tipos.get(col, 'TEXT')
                    valor_convertido = self.convertir_valor(valor, tipo_sqlite, col)
                    values.append(valor_convertido)
                
                try:
                    self.pg_cursor.execute(insert_sql, values)
                except Exception as e:
                    logger.warning(f"Error insertando registro en {tabla}: {e}")
                    # Intentar sin el campo problematico
                    if 'activo' in str(e):
                        cols_sin_activo = [c for c in columns if c.lower() != 'activo']
                        placeholders2 = ', '.join(['%s'] * len(cols_sin_activo))
                        column_names2 = ', '.join(cols_sin_activo)
                        insert_sql2 = f"INSERT INTO {schema}.{tabla} ({column_names2}) VALUES ({placeholders2})"
                        values2 = []
                        for col in cols_sin_activo:
                            valor = row[col]
                            tipo_sqlite = tipos.get(col, 'TEXT')
                            valor_convertido = self.convertir_valor(valor, tipo_sqlite, col)
                            values2.append(valor_convertido)
                        try:
                            self.pg_cursor.execute(insert_sql2, values2)
                        except Exception as e2:
                            logger.warning(f"Error en intento alternativo: {e2}")
            
            self.pg_conn.commit()
            logger.info(f"{len(rows)} registros migrados a {tabla}")
            sqlite_conn.close()
            
        except Exception as e:
            logger.error(f"Error migrando datos de {tabla}: {e}")

    def migrar_tenant_master(self):
        logger.info("Migrando base de datos maestra (tenant_master.db)")
        
        db_file = 'tenant_master.db'
        if not os.path.exists(db_file):
            logger.error(f"Archivo {db_file} no encontrado")
            return False
        
        tablas = self.obtener_tablas_sqlite(db_file)
        
        for tabla in tablas:
            logger.info(f"Migrando tabla: {tabla}")
            columns = self.obtener_esquema_tabla(db_file, tabla)
            
            if self.crear_tabla_postgresql(tabla, columns, 'public'):
                self.migrar_datos_tabla(db_file, tabla, 'public')
        
        return True

    def migrar_tenant(self, tenant_db, tenant_id, tenant_name):
        logger.info(f"Migrando tenant: {tenant_name} (ID: {tenant_id})")
        
        db_file = os.path.join('databases_tenants', tenant_db)
        if not os.path.exists(db_file):
            logger.warning(f"Archivo {db_file} no encontrado")
            return False
        
        schema_name = f"tenant_{tenant_id}"
        try:
            self.pg_cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            self.pg_conn.commit()
            logger.info(f"Schema {schema_name} creado")
        except Exception as e:
            logger.error(f"Error creando schema: {e}")
            return False
        
        tablas = self.obtener_tablas_sqlite(db_file)
        
        for tabla in tablas:
            logger.info(f"Migrando tabla: {tabla}")
            columns = self.obtener_esquema_tabla(db_file, tabla)
            
            if self.crear_tabla_postgresql(tabla, columns, schema_name):
                self.migrar_datos_tabla(db_file, tabla, schema_name)
        
        return True

    def obtener_tenants(self):
        db_file = 'tenant_master.db'
        if not os.path.exists(db_file):
            return []
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, nombre, base_datos FROM tenants ORDER BY id")
            tenants = cursor.fetchall()
        except:
            tenants = []
        
        conn.close()
        return tenants

    def migrar_todos_los_tenants(self):
        logger.info("INICIANDO MIGRACION COMPLETA")
        logger.info("=" * 50)
        
        if not self.conectar_postgresql():
            return False
        
        try:
            if not self.migrar_tenant_master():
                return False
            
            tenants = self.obtener_tenants()
            
            if not tenants:
                logger.warning("No se encontraron tenants para migrar")
                return True
            
            logger.info(f"Encontrados {len(tenants)} tenants")
            
            for tenant_id, tenant_name, db_file in tenants:
                self.migrar_tenant(db_file, tenant_id, tenant_name)
            
            logger.info("MIGRACION COMPLETADA")
            return True
            
        except Exception as e:
            logger.error(f"Error: {e}")
            self.pg_conn.rollback()
            return False
        finally:
            if self.pg_cursor:
                self.pg_cursor.close()
            if self.pg_conn:
                self.pg_conn.close()

def main():
    migrador = MigradorSQLiteAPostgreSQL()
    
    print("\nATENCION: Esto migrara TODOS los datos de SQLite a PostgreSQL")
    print(f"   PostgreSQL en puerto 5433")
    print(f"   Base de datos: panaderia_master")
    
    respuesta = input("\nContinuar con la migracion? (si/no): ")
    
    if respuesta.lower() not in ['si', 's', 'yes', 'y']:
        print("Migracion cancelada.")
        return
    
    success = migrador.migrar_todos_los_tenants()
    
    if success:
        print("\nMigracion completada con exito")
        print("Revise migracion.log para detalles")
    else:
        print("\nLa migracion fallo. Revise migracion.log")

if __name__ == "__main__":
    main()