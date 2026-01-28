from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from utils.db import get_db_connection
from utils.datetime_utils import get_local_now, format_date_local
from datetime import date
from functools import wraps

def requiere_permiso(nombre_permiso):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            permisos = session.get('permisos', [])
            if nombre_permiso not in permisos:
                flash('No tienes permiso para acceder a esta sección.', 'danger')
                return redirect(url_for('dashboard.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/diario')
def reporte_diario():
    """
    Muestra el reporte de entradas y salidas por fecha y sucursal
    """
    sucursal_id = request.args.get('sucursal_id', session.get('sucursal_id', 1), type=int)
    fecha_consulta = request.args.get('fecha', date.today().strftime('%Y-%m-%d'))
    
    print(f"DEBUG: Consultando sucursal {sucursal_id}, fecha {fecha_consulta}")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener información de la sucursal
        cursor.execute("SELECT id, nombre FROM sucursales WHERE id = %s", (sucursal_id,))
        sucursal = cursor.fetchone()
        
        if not sucursal:
            sucursal = {'id': 1, 'nombre': 'Matriz'}
        
        # Obtener todas las sucursales para el selector
        cursor.execute("SELECT id, nombre FROM sucursales ORDER BY id")
        sucursales = cursor.fetchall()
        
        # === 1. SALIDAS DE CLIENTES ===
        cursor.execute("""
            SELECT 
                ns.folio,
                ns.fecha,
                CONCAT(c.nombre, ' ', c.apellido1, ' ', IFNULL(c.apellido2, '')) as cliente_nombre,
                r.direccion_obra,
                GROUP_CONCAT(
                    CONCAT(p.nombre_pieza, ' (', nsd.cantidad, ')')
                    ORDER BY p.nombre_pieza SEPARATOR ', '
                ) as piezas_detalle
            FROM notas_salida ns
            JOIN rentas r ON ns.renta_id = r.id
            JOIN clientes c ON r.cliente_id = c.id
            JOIN notas_salida_detalle nsd ON ns.id = nsd.nota_salida_id
            JOIN piezas p ON nsd.id_pieza = p.id_pieza
            WHERE r.id_sucursal = %s 
            AND DATE(ns.fecha) = %s
            AND ns.renta_id IS NOT NULL
            GROUP BY ns.id, ns.folio, ns.fecha, c.nombre, c.apellido1, c.apellido2, r.direccion_obra
            ORDER BY ns.fecha DESC
        """, (sucursal_id, fecha_consulta))
        salidas_clientes = cursor.fetchall()
        print(f"DEBUG: Salidas clientes encontradas: {len(salidas_clientes)}")
        
        # === 2. ENTRADAS DE CLIENTES ===
        cursor.execute("""
            SELECT 
                ne.folio,
                ne.fecha_entrada_real as fecha,
                CONCAT(c.nombre, ' ', c.apellido1, ' ', IFNULL(c.apellido2, '')) as cliente_nombre,
                r.direccion_obra,
                GROUP_CONCAT(
                    CONCAT(p.nombre_pieza, ' (', ned.cantidad_recibida, ')')
                    ORDER BY p.nombre_pieza SEPARATOR ', '
                ) as piezas_detalle
            FROM notas_entrada ne
            JOIN rentas r ON ne.renta_id = r.id
            JOIN clientes c ON r.cliente_id = c.id
            JOIN notas_entrada_detalle ned ON ne.id = ned.nota_entrada_id
            JOIN piezas p ON ned.id_pieza = p.id_pieza
            WHERE r.id_sucursal = %s 
            AND DATE(ne.fecha_entrada_real) = %s
            AND ne.renta_id IS NOT NULL
            GROUP BY ne.id, ne.folio, ne.fecha_entrada_real, c.nombre, c.apellido1, c.apellido2, r.direccion_obra
            ORDER BY ne.fecha_entrada_real DESC
        """, (sucursal_id, fecha_consulta))
        entradas_clientes = cursor.fetchall()
        print(f"DEBUG: Entradas clientes encontradas: {len(entradas_clientes)}")
        
        # === 3. SALIDAS EXTRAS ===
        salidas_extras = []
        
        # 3.1 Transferencias enviadas
        cursor.execute("""
            SELECT 
                'transferencia' as tipo,
                mi.folio_nota_salida as folio,
                mi.fecha,
                CONCAT('Transferencia a ', sd.nombre) as descripcion,
                GROUP_CONCAT(
                    CONCAT(p.nombre_pieza, ' (', mi.cantidad, ')')
                    ORDER BY p.nombre_pieza SEPARATOR ', '
                ) as piezas_detalle
            FROM movimientos_inventario mi
            JOIN piezas p ON mi.id_pieza = p.id_pieza
            JOIN sucursales sd ON mi.sucursal_destino = sd.id
            WHERE mi.id_sucursal = %s 
            AND DATE(mi.fecha) = %s
            AND mi.tipo_movimiento = 'transferencia_salida'
            AND mi.folio_nota_salida IS NOT NULL
            GROUP BY mi.folio_nota_salida, mi.fecha, sd.nombre
            ORDER BY mi.fecha DESC
        """, (sucursal_id, fecha_consulta))
        salidas_extras.extend(cursor.fetchall())
        
        # 3.2 Equipos enviados a reparación
        cursor.execute("""
            SELECT 
                'reparacion' as tipo,
                mi.folio_nota_salida as folio,
                mi.fecha,
                'Equipos enviados a reparación' as descripcion,
                GROUP_CONCAT(
                    CONCAT(p.nombre_pieza, ' (', mi.cantidad, ')')
                    ORDER BY p.nombre_pieza SEPARATOR ', '
                ) as piezas_detalle
            FROM movimientos_inventario mi
            JOIN piezas p ON mi.id_pieza = p.id_pieza
            WHERE mi.id_sucursal = %s 
            AND DATE(mi.fecha) = %s
            AND mi.tipo_movimiento = 'reparacion_lote'
            AND mi.folio_nota_salida IS NOT NULL
            GROUP BY mi.folio_nota_salida, mi.fecha
            ORDER BY mi.fecha DESC
        """, (sucursal_id, fecha_consulta))
        salidas_extras.extend(cursor.fetchall())
        
        # 3.3 Salidas internas
        cursor.execute("""
            SELECT 
                'salida_interna' as tipo,
                CONCAT('SUC', si.id_sucursal, '-', LPAD(si.folio_sucursal, 4, '0')) as folio,
                si.fecha_salida as fecha,
                CONCAT('Salida interna - ', si.responsable_entrega) as descripcion,
                GROUP_CONCAT(
                    CONCAT(p.nombre_pieza, ' (', sid.cantidad, ')')
                    ORDER BY p.nombre_pieza SEPARATOR ', '
                ) as piezas_detalle
            FROM salidas_internas si
            JOIN salidas_internas_detalle sid ON si.id = sid.salida_interna_id
            JOIN piezas p ON sid.id_pieza = p.id_pieza
            WHERE si.id_sucursal = %s 
            AND DATE(si.fecha_salida) = %s
            GROUP BY si.id, si.folio_sucursal, si.fecha_salida, si.responsable_entrega, si.id_sucursal
            ORDER BY si.fecha_salida DESC
        """, (sucursal_id, fecha_consulta))
        salidas_extras.extend(cursor.fetchall())
        
        # === 4. ENTRADAS EXTRAS ===
        entradas_extras = []
        
        # 4.1 Transferencias recibidas
        cursor.execute("""
            SELECT 
                'transferencia' as tipo,
                mi.folio_nota_entrada as folio,
                mi.fecha,
                'Transferencia recibida' as descripcion,
                GROUP_CONCAT(
                    CONCAT(p.nombre_pieza, ' (', mi.cantidad, ')')
                    ORDER BY p.nombre_pieza SEPARATOR ', '
                ) as piezas_detalle
            FROM movimientos_inventario mi
            JOIN piezas p ON mi.id_pieza = p.id_pieza
            WHERE mi.id_sucursal = %s 
            AND DATE(mi.fecha) = %s
            AND mi.tipo_movimiento = 'transferencia_entrada'
            AND mi.folio_nota_entrada IS NOT NULL
            GROUP BY mi.folio_nota_entrada, mi.fecha
            ORDER BY mi.fecha DESC
        """, (sucursal_id, fecha_consulta))
        entradas_extras.extend(cursor.fetchall())
        
        # 4.2 Altas de equipos nuevos
        cursor.execute("""
            SELECT 
                'alta_equipo' as tipo,
                mi.folio_nota_entrada as folio,
                mi.fecha,
                'Alta de equipos nuevos' as descripcion,
                GROUP_CONCAT(
                    CONCAT(p.nombre_pieza, ' (', mi.cantidad, ')')
                    ORDER BY p.nombre_pieza SEPARATOR ', '
                ) as piezas_detalle
            FROM movimientos_inventario mi
            JOIN piezas p ON mi.id_pieza = p.id_pieza
            WHERE mi.id_sucursal = %s 
            AND DATE(mi.fecha) = %s
            AND mi.tipo_movimiento = 'alta_equipo'
            AND mi.folio_nota_entrada IS NOT NULL
            GROUP BY mi.folio_nota_entrada, mi.fecha
            ORDER BY mi.fecha DESC
        """, (sucursal_id, fecha_consulta))
        entradas_extras.extend(cursor.fetchall())
        
        # Ordenar entradas y salidas extras por fecha
        salidas_extras = sorted(salidas_extras, key=lambda x: x['fecha'], reverse=True)
        entradas_extras = sorted(entradas_extras, key=lambda x: x['fecha'], reverse=True)
        
        print(f"DEBUG: Total salidas extras: {len(salidas_extras)}")
        print(f"DEBUG: Total entradas extras: {len(entradas_extras)}")
        
        cursor.close()
        conn.close()
        
        return render_template('reportes/reportes.html', 
                             salidas_clientes=salidas_clientes,
                             entradas_clientes=entradas_clientes,
                             salidas_extras=salidas_extras,
                             entradas_extras=entradas_extras,
                             sucursal=sucursal,
                             sucursales=sucursales,
                             fecha_consulta=fecha_consulta,
                             fecha_formato=format_date_local(get_local_now(), '%d/%m/%Y'))
        
    except Exception as e:
        print(f'Error en reporte diario: {e}')
        return render_template('reportes/reportes.html', 
                             error='Error al generar el reporte',
                             sucursal=sucursal,
                             sucursales=sucursales if 'sucursales' in locals() else [],
                             fecha_consulta=fecha_consulta,
                             fecha_formato=format_date_local(get_local_now(), '%d/%m/%Y'))