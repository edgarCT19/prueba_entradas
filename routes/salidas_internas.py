# ======================= IMPORTS =======================
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import timedelta
from utils.db import get_db_connection
from functools import wraps
from utils.datetime_utils import get_local_now

# Importar función de folios del módulo inventario
from routes.inventario import obtener_siguiente_folio_nota_sucursal

# ======================= BLUEPRINT =======================
salidas_internas_bp = Blueprint('salidas_internas', __name__, url_prefix='/salidas-internas')

def requiere_permiso(nombre_permiso):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Aquí puedes agregar la lógica de permisos si es necesario
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ======================= LISTADO DE SALIDAS INTERNAS =======================
@salidas_internas_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener sucursal del usuario desde la sesión
    sucursal_id_usuario = session.get('sucursal_id')
    rol_id = session.get('rol_id')
    
    # Determinar qué sucursal filtrar
    sucursal_filtro = request.args.get('sucursal_id')
    sucursal_actual = None
    
    # Construir WHERE clause para sucursal
    where_sucursal = ""
    params_sucursal = []
    
    if rol_id == 2:  # Admin
        if sucursal_filtro and sucursal_filtro != 'todas':
            where_sucursal = "WHERE si.id_sucursal = %s"
            params_sucursal = [sucursal_filtro]
            cursor.execute("SELECT id, nombre FROM sucursales WHERE id = %s", (sucursal_filtro,))
            sucursal_data = cursor.fetchone()
            sucursal_actual = {'id': sucursal_filtro, 'nombre': sucursal_data['nombre']} if sucursal_data else None
        else:
            sucursal_actual = {'id': 'todas', 'nombre': 'Todas las Sucursales'}
        
        # Obtener todas las sucursales para el filtro
        cursor.execute("SELECT id, nombre FROM sucursales ORDER BY nombre")
        sucursales = cursor.fetchall()
    else:
        where_sucursal = "WHERE si.id_sucursal = %s"
        params_sucursal = [sucursal_id_usuario]
        cursor.execute("SELECT id, nombre FROM sucursales WHERE id = %s", (sucursal_id_usuario,))
        sucursal_data = cursor.fetchone()
        sucursal_actual = {'id': sucursal_id_usuario, 'nombre': sucursal_data['nombre']} if sucursal_data else None
        sucursales = []

    # Consulta principal de salidas internas
    cursor.execute(f"""
        SELECT 
            si.id, si.folio_sucursal, si.fecha_salida, si.responsable_entrega,
            si.observaciones, si.estado, si.fecha_finalizacion,
            s.nombre as sucursal_nombre, s.id as id_sucursal,
            COUNT(sid.id) as total_productos,
            SUM(sid.cantidad) as cantidad_total_equipos
        FROM salidas_internas si
        JOIN sucursales s ON si.id_sucursal = s.id
        LEFT JOIN salidas_internas_detalle sid ON si.id = sid.salida_interna_id
        {where_sucursal}
        GROUP BY si.id, si.folio_sucursal, si.fecha_salida, si.responsable_entrega,
                 si.observaciones, si.estado, si.fecha_finalizacion, s.nombre, s.id
        ORDER BY si.fecha_salida DESC, si.folio_sucursal DESC
    """, params_sucursal)
    
    salidas_internas = cursor.fetchall()

    # Obtener productos disponibles en la sucursal para el modal
    if sucursal_id_usuario:
        cursor.execute("""
            SELECT p.id_pieza, p.nombre_pieza, 
                   COALESCE(inv.disponibles, 0) as disponibles
            FROM piezas p
            LEFT JOIN inventario_sucursal inv ON p.id_pieza = inv.id_pieza 
                                               AND inv.id_sucursal = %s
            WHERE COALESCE(inv.disponibles, 0) > 0
            ORDER BY p.nombre_pieza
        """, (sucursal_id_usuario,))
        productos_disponibles = cursor.fetchall()
    else:
        productos_disponibles = []

    cursor.close()
    conn.close()

    return render_template(
        'salidas_internas/index.html',
        salidas_internas=salidas_internas,
        productos_disponibles=productos_disponibles,
        sucursal_actual=sucursal_actual,
        sucursales=sucursales if rol_id == 2 else [],
        es_admin=(rol_id == 2),
        sucursal_id_usuario=sucursal_id_usuario
    )

# ======================= CREAR SALIDA INTERNA =======================
@salidas_internas_bp.route('/crear', methods=['POST'])
def crear_salida_interna():
    try:
        data = request.get_json()
        sucursal_id = data.get('sucursal_id')
        responsable_entrega = data.get('responsable_entrega', '').strip()
        observaciones = data.get('observaciones', '').strip()
        productos = data.get('productos', [])
        usuario_id = session.get('user_id')

        if not sucursal_id or not responsable_entrega or not productos:
            return jsonify({'success': False, 'error': 'Datos incompletos'})

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Obtener siguiente folio consecutivo del sistema
            folio_sucursal = obtener_siguiente_folio_nota_sucursal(cursor, sucursal_id)
            # Validar que el folio sea un entero
            try:
                folio_int = int(folio_sucursal)
            except Exception:
                return jsonify({'success': False, 'error': 'Error: El folio generado no es válido.'})

            # Crear salida interna
            cursor.execute("""
                INSERT INTO salidas_internas 
                (id_sucursal, folio_sucursal, fecha_salida, responsable_entrega, observaciones, estado, usuario_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (sucursal_id, folio_int, get_local_now(), responsable_entrega, observaciones, 'activa', usuario_id))

            salida_id = cursor.lastrowid

            # Procesar cada producto
            for producto in productos:
                id_pieza = producto.get('id_pieza')
                cantidad = producto.get('cantidad')

                if not id_pieza or not cantidad or cantidad <= 0:
                    continue

                # Verificar inventario disponible
                cursor.execute("""
                    SELECT disponibles, rentadas 
                    FROM inventario_sucursal 
                    WHERE id_pieza = %s AND id_sucursal = %s
                """, (id_pieza, sucursal_id))

                inventario = cursor.fetchone()
                if not inventario or inventario['disponibles'] < cantidad:
                    conn.rollback()
                    cursor.execute("SELECT nombre_pieza FROM piezas WHERE id_pieza = %s", (id_pieza,))
                    pieza_info = cursor.fetchone()
                    nombre_pieza = pieza_info['nombre_pieza'] if pieza_info else f'ID {id_pieza}'
                    return jsonify({
                        'success': False,
                        'error': f'No hay suficiente inventario disponible de {nombre_pieza}'
                    })

                # Insertar detalle de salida
                cursor.execute("""
                    INSERT INTO salidas_internas_detalle 
                    (salida_interna_id, id_pieza, cantidad)
                    VALUES (%s, %s, %s)
                """, (salida_id, id_pieza, cantidad))

                # Actualizar inventario: mover de disponibles a rentadas
                nuevos_disponibles = inventario['disponibles'] - cantidad
                nuevas_rentadas = inventario['rentadas'] + cantidad

                cursor.execute("""
                    UPDATE inventario_sucursal 
                    SET disponibles = %s, rentadas = %s 
                    WHERE id_pieza = %s AND id_sucursal = %s
                """, (nuevos_disponibles, nuevas_rentadas, id_pieza, sucursal_id))

                # Registrar movimiento en historial
                cursor.execute("""
                    INSERT INTO movimientos_inventario 
                    (id_pieza, id_sucursal, tipo_movimiento, cantidad, descripcion, usuario)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_pieza, sucursal_id, 'salida_interna', cantidad,
                    f'Salida interna - Folio: SUC{sucursal_id}-{folio_int:04d} - Responsable: {responsable_entrega}',
                    usuario_id
                ))

            conn.commit()

            return jsonify({
                'success': True,
                'message': f'Salida interna creada correctamente - Folio: SUC{sucursal_id}-{folio_int:04d}',
                'folio': f'SUC{sucursal_id}-{folio_int:04d}',
                'salida_id': salida_id
            })
            
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': f'Error al crear salida interna: {str(e)}'})
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error en el procesamiento: {str(e)}'})

# ======================= FINALIZAR SALIDA INTERNA =======================
@salidas_internas_bp.route('/finalizar/<int:salida_id>', methods=['POST'])
def finalizar_salida_interna(salida_id):
    try:
        data = request.get_json()
        tipo_finalizacion = data.get('tipo')  # 'regreso' o 'no_regreso'
        observaciones_finalizacion = data.get('observaciones', '').strip()
        usuario_id = session.get('user_id')

        if not tipo_finalizacion or tipo_finalizacion not in ['regreso', 'no_regreso']:
            return jsonify({'success': False, 'error': 'Tipo de finalización inválido'})

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Obtener datos de la salida interna
            cursor.execute("""
                SELECT si.*, s.nombre as sucursal_nombre
                FROM salidas_internas si
                JOIN sucursales s ON si.id_sucursal = s.id
                WHERE si.id = %s AND si.estado = 'activa'
            """, (salida_id,))
            
            salida = cursor.fetchone()
            if not salida:
                return jsonify({'success': False, 'error': 'Salida interna no encontrada o ya finalizada'})
            
            # Obtener productos de la salida
            cursor.execute("""
                SELECT sid.*, p.nombre_pieza
                FROM salidas_internas_detalle sid
                JOIN piezas p ON sid.id_pieza = p.id_pieza
                WHERE sid.salida_interna_id = %s
            """, (salida_id,))
            
            productos_salida = cursor.fetchall()
            
            # Procesar según el tipo de finalización
            for producto in productos_salida:
                id_pieza = producto['id_pieza']
                cantidad = producto['cantidad']
                
                # Obtener inventario actual
                cursor.execute("""
                    SELECT total, disponibles, rentadas 
                    FROM inventario_sucursal 
                    WHERE id_pieza = %s AND id_sucursal = %s
                """, (id_pieza, salida['id_sucursal']))
                
                inventario = cursor.fetchone()
                if not inventario:
                    continue
                
                if tipo_finalizacion == 'regreso':
                    # El equipo regresó: mover de rentadas a disponibles
                    nuevas_rentadas = max(0, inventario['rentadas'] - cantidad)
                    nuevos_disponibles = inventario['disponibles'] + cantidad
                    
                    cursor.execute("""
                        UPDATE inventario_sucursal 
                        SET disponibles = %s, rentadas = %s 
                        WHERE id_pieza = %s AND id_sucursal = %s
                    """, (nuevos_disponibles, nuevas_rentadas, id_pieza, salida['id_sucursal']))
                    
                    # Registrar movimiento
                    cursor.execute("""
                        INSERT INTO movimientos_inventario 
                        (id_pieza, id_sucursal, tipo_movimiento, cantidad, descripcion, usuario)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        id_pieza, salida['id_sucursal'], 'retorno_salida_interna', cantidad,
                        f'Retorno de salida interna - Folio: SUC{salida["id_sucursal"]}-{salida["folio_sucursal"]:04d} - {observaciones_finalizacion}',
                        usuario_id
                    ))
                    
                else:  # no_regreso
                    # El equipo no regresó: descontar del total y de rentadas
                    nuevo_total = max(0, inventario['total'] - cantidad)
                    nuevas_rentadas = max(0, inventario['rentadas'] - cantidad)
                    
                    cursor.execute("""
                        UPDATE inventario_sucursal 
                        SET total = %s, rentadas = %s 
                        WHERE id_pieza = %s AND id_sucursal = %s
                    """, (nuevo_total, nuevas_rentadas, id_pieza, salida['id_sucursal']))
                    
                    # Registrar movimiento
                    cursor.execute("""
                        INSERT INTO movimientos_inventario 
                        (id_pieza, id_sucursal, tipo_movimiento, cantidad, descripcion, usuario)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        id_pieza, salida['id_sucursal'], 'perdida_salida_interna', cantidad,
                        f'Pérdida de salida interna - Folio: SUC{salida["id_sucursal"]}-{salida["folio_sucursal"]:04d} - {observaciones_finalizacion}',
                        usuario_id
                    ))
            
            # Actualizar estado de la salida interna
            cursor.execute("""
                UPDATE salidas_internas 
                SET estado = %s, fecha_finalizacion = %s, observaciones_finalizacion = %s, usuario_finalizacion = %s
                WHERE id = %s
            """, (
                'finalizada_regreso' if tipo_finalizacion == 'regreso' else 'finalizada_no_regreso',
                get_local_now(),
                observaciones_finalizacion,
                usuario_id,
                salida_id
            ))
            
            conn.commit()
            
            mensaje_tipo = 'con regreso de equipo' if tipo_finalizacion == 'regreso' else 'sin regreso de equipo'
            return jsonify({
                'success': True,
                'message': f'Salida interna finalizada correctamente ({mensaje_tipo})'
            })
            
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': f'Error al finalizar salida interna: {str(e)}'})
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error en el procesamiento: {str(e)}'})

# ======================= OBTENER DETALLE DE SALIDA INTERNA =======================
@salidas_internas_bp.route('/detalle/<int:salida_id>')
def obtener_detalle_salida(salida_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener datos de la salida
        cursor.execute("""
            SELECT si.*, s.nombre as sucursal_nombre
            FROM salidas_internas si
            JOIN sucursales s ON si.id_sucursal = s.id
            WHERE si.id = %s
        """, (salida_id,))
        
        salida = cursor.fetchone()
        if not salida:
            return jsonify({'success': False, 'error': 'Salida interna no encontrada'})
        
        # Obtener productos de la salida
        cursor.execute("""
            SELECT sid.*, p.nombre_pieza, p.codigo_pieza
            FROM salidas_internas_detalle sid
            JOIN piezas p ON sid.id_pieza = p.id_pieza
            WHERE sid.salida_interna_id = %s
            ORDER BY p.nombre_pieza
        """, (salida_id,))
        
        productos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'salida': salida,
            'productos': productos
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al obtener detalle: {str(e)}'})