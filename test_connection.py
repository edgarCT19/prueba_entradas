#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la conexión a la base de datos AWS RDS
"""

import mysql.connector
from mysql.connector import Error
import sys

# Configuración de conexión
DB_CONFIG = {
    'host': 'database-1.cf0ey64ia6yt.us-east-2.rds.amazonaws.com',
    'user': 'admin',
    'password': '12345678',
    'database': 'andamiosdb',
    'port': 3306,
    'connection_timeout': 10,
    'autocommit': True,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def test_connection():
    """Prueba la conexión a la base de datos"""
    connection = None
    cursor = None
    
    try:
        print("🔄 Intentando conectar a AWS RDS...")
        print(f"   Host: {DB_CONFIG['host']}")
        print(f"   Base de datos: {DB_CONFIG['database']}")
        print(f"   Usuario: {DB_CONFIG['user']}")
        print()
        
        # Intentar conexión
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ ¡Conexión exitosa!")
            
            # Obtener información del servidor
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            db_version = cursor.fetchone()
            print(f"   Versión MySQL: {db_version[0]}")
            
            # Verificar la base de datos actual
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()
            print(f"   Base de datos actual: {current_db[0]}")
            
            # Listar algunas tablas
            cursor.execute("SHOW TABLES LIMIT 5")
            tables = cursor.fetchall()
            print(f"   Primeras 5 tablas:")
            for table in tables:
                print(f"     - {table[0]}")
                
            print()
            print("🎉 La conexión funciona correctamente!")
            return True
            
    except Error as e:
        print("❌ Error de conexión:")
        print(f"   Código de error: {e.errno}")
        print(f"   Mensaje: {e.msg}")
        
        # Errores comunes y soluciones
        if e.errno == 1045:
            print("\n💡 Posibles soluciones:")
            print("   - Verificar usuario y contraseña")
            print("   - Verificar que el usuario tenga permisos")
        elif e.errno == 2003:
            print("\n💡 Posibles soluciones:")
            print("   - Verificar que el host esté correcto")
            print("   - Verificar configuración de Security Groups en AWS")
            print("   - Verificar que el puerto 3306 esté abierto")
        elif e.errno == 1049:
            print("\n💡 Posibles soluciones:")
            print("   - Verificar que la base de datos 'andamiosdb' exista")
        else:
            print("\n💡 Revisa:")
            print("   - Configuración de red en AWS RDS")
            print("   - Security Groups y reglas de entrada")
            print("   - VPC y subnets si aplica")
        
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("🔒 Conexión cerrada.")

def test_flask_sqlalchemy():
    """Prueba la conexión usando SQLAlchemy (como en Flask)"""
    try:
        from sqlalchemy import create_engine, text
        
        print("\n" + "="*50)
        print("🔄 Probando conexión SQLAlchemy...")
        
        # URI de conexión de SQLAlchemy
        database_uri = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        
        engine = create_engine(database_uri, echo=False)
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'SQLAlchemy conectado correctamente!' as mensaje"))
            message = result.fetchone()
            print(f"✅ {message[0]}")
            
            # Verificar tablas
            result = conn.execute(text("SHOW TABLES LIMIT 3"))
            tables = result.fetchall()
            print(f"   Tablas encontradas: {len(tables)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en SQLAlchemy: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 PRUEBA DE CONEXIÓN A BASE DE DATOS AWS RDS")
    print("="*50)
    
    # Probar con mysql-connector-python
    success1 = test_connection()
    
    # Probar con SQLAlchemy
    success2 = test_flask_sqlalchemy()
    
    print("\n" + "="*50)
    print("📋 RESUMEN:")
    print(f"   MySQL Connector: {'✅ OK' if success1 else '❌ ERROR'}")
    print(f"   SQLAlchemy:      {'✅ OK' if success2 else '❌ ERROR'}")
    
    if success1 and success2:
        print("\n🎉 ¡Todo funciona correctamente!")
        print("   Tu aplicación Flask debería poder conectarse sin problemas.")
    else:
        print("\n⚠️  Hay problemas de conectividad.")
        print("   Revisa la configuración de AWS RDS y los Security Groups.")