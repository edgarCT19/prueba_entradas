from flask import Blueprint, render_template, request, jsonify, session
from utils.db import get_db_connection
from datetime import datetime, date
import traceback

caja_bp = Blueprint('caja', __name__, url_prefix='/caja')

# ============================================================================
# FUNCIÓN HELPER PARA REGISTRAR MOVIMIENTOS AUTOMÁTICOS
# ============================================================================

def registrar_movimiento_automatico(tipo, concepto, monto, metodo_pago, usuario_id, sucursal_id, 
                                  referencia_tabla, referencia_id, numero_seguimiento=None, observaciones=None):
    """
    Función helper para registrar automáticamente movimientos de caja cuando se realizan pagos EN EFECTIVO.
    IMPORTANTE: Solo registra movimientos cuando el método de pago es EFECTIVO.
    
    Args:
        tipo: 'ingreso' o 'egreso'
        concepto: Descripción del movimiento
        monto: Cantidad del movimiento
        metodo_pago: Método de pago utilizado (solo se registra si es 'EFECTIVO')
        usuario_id: ID del usuario que realiza la acción
        sucursal_id: ID de la sucursal
        referencia_tabla: 'prefacturas', 'notas_cobro_extra', 'notas_cobro_retraso'
        referencia_id: ID del registro que genera el movimiento
        numero_seguimiento: Opcional, número de seguimiento (no aplicable para efectivo)
        observaciones: Opcional, observaciones adicionales
    
    Returns:
        dict: {'success': bool, 'movimiento_id': int, 'error': str, 'registered': bool}
    """
    try:
        # IMPORTANTE: Solo registrar en caja si el pago es en EFECTIVO
        if metodo_pago != 'EFECTIVO':
            return {'success': True, 'registered': False, 'message': f'Pago por {metodo_pago} no se registra en movimientos de caja (solo efectivo)'}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insertar movimiento automático solo para EFECTIVO
        cursor.execute("""
            INSERT INTO movimientos_caja (
                fecha, hora, tipo, concepto, monto, metodo_pago, 
                observaciones, tipo_movimiento, 
                referencia_tabla, referencia_id, usuario_id, sucursal_id
            ) VALUES (
                CURDATE(), CURTIME(), %s, %s, %s, 'EFECTIVO', 
                %s, 'automatico', %s, %s, %s, %s
            )
        """, (
            tipo, concepto, monto, observaciones, 
            referencia_tabla, referencia_id, usuario_id, sucursal_id
        ))
        
        movimiento_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True, 'movimiento_id': movimiento_id, 'registered': True}
        
    except Exception as e:
        print(f"Error al registrar movimiento automático: {e}")
        return {'success': False, 'error': str(e)}

# ============================================================================
# ENDPOINTS PRINCIPALES
# ============================================================================

@caja_bp.route('/')
def movimientos_caja():
    """Vista principal del módulo de caja"""
    return render_template('caja/movimiento_caja.html')

@caja_bp.route('/api/movimientos')
def obtener_movimientos():
    """Obtiene movimientos de caja con filtros"""
    try:
        # Parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin') 
        tipo = request.args.get('tipo')  # 'ingreso', 'egreso', ''
        tipo_movimiento = request.args.get('tipo_movimiento')  # 'manual', 'automatico', ''
        metodo_pago = request.args.get('metodo_pago')
        sucursal_id = session.get('sucursal_id', 1)
        
        # Si no hay fechas, usar fecha actual
        if not fecha_inicio:
            fecha_inicio = date.today().strftime('%Y-%m-%d')
        if not fecha_fin:
            fecha_fin = fecha_inicio
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Construir consulta dinámica
        where_clauses = ["mc.sucursal_id = %s", "mc.fecha BETWEEN %s AND %s"]
        params = [sucursal_id, fecha_inicio, fecha_fin]
        
        if tipo:
            where_clauses.append("mc.tipo = %s")
            params.append(tipo)
            
        if tipo_movimiento:
            where_clauses.append("mc.tipo_movimiento = %s")
            params.append(tipo_movimiento)
            
        if metodo_pago:
            where_clauses.append("mc.metodo_pago = %s")
            params.append(metodo_pago)
        
        where_sql = " AND ".join(where_clauses)
        
        # Consulta principal con JOIN para obtener nombre del usuario
        cursor.execute(f"""
            SELECT 
                mc.id,
                mc.fecha,
                mc.hora,
                mc.tipo,
                mc.concepto,
                mc.monto,
                mc.metodo_pago,
                mc.numero_seguimiento,
                mc.observaciones,
                mc.tipo_movimiento,
                mc.referencia_tabla,
                mc.referencia_id,
                CONCAT(u.nombre, ' ', u.apellido1) as usuario_nombre,
                mc.created_at
            FROM movimientos_caja mc
            LEFT JOIN usuarios u ON mc.usuario_id = u.id
            WHERE {where_sql}
            ORDER BY mc.fecha DESC, mc.hora DESC
        """, params)
        
        movimientos = cursor.fetchall()
        
        # Formatear datos para el frontend
        for mov in movimientos:
            mov['fecha_formateada'] = mov['fecha'].strftime('%d/%m/%Y')
            mov['hora_formateada'] = mov['hora'].strftime('%H:%M')
            mov['monto_formateado'] = f"{float(mov['monto']):,.2f}"
            
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'movimientos': movimientos
        })
        
    except Exception as e:
        print(f"Error al obtener movimientos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@caja_bp.route('/api/resumen')
def obtener_resumen():
    """Obtiene resumen de ingresos/egresos del día o rango de fechas"""
    try:
        fecha_inicio = request.args.get('fecha_inicio', date.today().strftime('%Y-%m-%d'))
        fecha_fin = request.args.get('fecha_fin', fecha_inicio)
        sucursal_id = session.get('sucursal_id', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener totales por tipo
        cursor.execute("""
            SELECT 
                tipo,
                COALESCE(SUM(monto), 0) as total,
                COUNT(*) as cantidad
            FROM movimientos_caja 
            WHERE sucursal_id = %s AND fecha BETWEEN %s AND %s
            GROUP BY tipo
        """, (sucursal_id, fecha_inicio, fecha_fin))
        
        resultados = cursor.fetchall()
        
        # Inicializar totales
        total_ingresos = 0.0
        total_egresos = 0.0
        count_ingresos = 0
        count_egresos = 0
        
        for resultado in resultados:
            if resultado['tipo'] == 'ingreso':
                total_ingresos = float(resultado['total'])
                count_ingresos = resultado['cantidad']
            elif resultado['tipo'] == 'egreso':
                total_egresos = float(resultado['total'])
                count_egresos = resultado['cantidad']
        
        saldo_neto = total_ingresos - total_egresos
        
        # Obtener desglose por método de pago (solo para el día actual)
        if fecha_inicio == fecha_fin == date.today().strftime('%Y-%m-%d'):
            cursor.execute("""
                SELECT 
                    metodo_pago,
                    tipo,
                    COALESCE(SUM(monto), 0) as total
                FROM movimientos_caja 
                WHERE sucursal_id = %s AND fecha = %s
                GROUP BY metodo_pago, tipo
                ORDER BY metodo_pago, tipo
            """, (sucursal_id, fecha_inicio))
            
            desglose_metodos = cursor.fetchall()
        else:
            desglose_metodos = []
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'resumen': {
                'total_ingresos': total_ingresos,
                'total_egresos': total_egresos,
                'saldo_neto': saldo_neto,
                'count_ingresos': count_ingresos,
                'count_egresos': count_egresos,
                'desglose_metodos': desglose_metodos,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
        })
        
    except Exception as e:
        print(f"Error al obtener resumen: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@caja_bp.route('/api/movimiento', methods=['POST'])
def crear_movimiento_manual():
    """Crear un nuevo movimiento manual de caja"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['tipo', 'concepto', 'monto', 'metodo_pago']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Campo {field} es requerido'}), 400
        
        # Obtener datos del formulario
        tipo = data.get('tipo')
        concepto = data.get('concepto', '').strip()
        monto = float(data.get('monto', 0))
        metodo_pago = data.get('metodo_pago')
        numero_seguimiento = data.get('numero_seguimiento', '').strip()
        observaciones = data.get('observaciones', '').strip()
        
        # Validaciones
        if tipo not in ['ingreso', 'egreso']:
            return jsonify({'success': False, 'error': 'Tipo de movimiento inválido'}), 400
            
        if monto <= 0:
            return jsonify({'success': False, 'error': 'El monto debe ser mayor a 0'}), 400
            
        # Movimientos de caja solo aceptan EFECTIVO
        if metodo_pago != 'EFECTIVO':
            return jsonify({'success': False, 'error': 'Los movimientos de caja solo aceptan pagos en EFECTIVO'}), 400
        
        # Datos del usuario y sucursal
        usuario_id = session.get('user_id')
        sucursal_id = session.get('sucursal_id', 1)
        
        if not usuario_id:
            return jsonify({'success': False, 'error': 'Usuario no autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insertar movimiento manual en efectivo
        cursor.execute("""
            INSERT INTO movimientos_caja (
                fecha, hora, tipo, concepto, monto, metodo_pago, 
                observaciones, tipo_movimiento, 
                usuario_id, sucursal_id
            ) VALUES (
                CURDATE(), CURTIME(), %s, %s, %s, 'EFECTIVO', 
                %s, 'manual', %s, %s
            )
        """, (
            tipo, concepto, monto,
            observaciones if observaciones else None,
            usuario_id, sucursal_id
        ))
        
        movimiento_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Movimiento de {tipo} registrado exitosamente',
            'movimiento_id': movimiento_id
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': 'Monto inválido'}), 400
    except Exception as e:
        print(f"Error al crear movimiento manual: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@caja_bp.route('/api/movimiento/<int:movimiento_id>')
def obtener_detalle_movimiento(movimiento_id):
    """Obtiene el detalle completo de un movimiento"""
    try:
        sucursal_id = session.get('sucursal_id', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                mc.*,
                CONCAT(u.nombre, ' ', u.apellido1, ' ', u.apellido2) as usuario_completo,
                s.nombre as sucursal_nombre
            FROM movimientos_caja mc
            LEFT JOIN usuarios u ON mc.usuario_id = u.id
            LEFT JOIN sucursales s ON mc.sucursal_id = s.id
            WHERE mc.id = %s AND mc.sucursal_id = %s
        """, (movimiento_id, sucursal_id))
        
        movimiento = cursor.fetchone()
        
        if not movimiento:
            return jsonify({'success': False, 'error': 'Movimiento no encontrado'}), 404
        
        # Si es movimiento automático, obtener datos de la referencia
        referencia_info = None
        if movimiento['tipo_movimiento'] == 'automatico' and movimiento['referencia_tabla']:
            try:
                if movimiento['referencia_tabla'] == 'prefacturas':
                    cursor.execute("""
                        SELECT p.id, p.tipo, p.monto, r.id as renta_id, 
                               CONCAT(c.nombre, ' ', c.apellido1) as cliente_nombre
                        FROM prefacturas p
                        JOIN rentas r ON p.renta_id = r.id
                        JOIN clientes c ON r.cliente_id = c.id
                        WHERE p.id = %s
                    """, (movimiento['referencia_id'],))
                elif movimiento['referencia_tabla'] == 'notas_cobro_extra':
                    cursor.execute("""
                        SELECT nce.id, nce.tipo, nce.total as monto, ne.folio, r.id as renta_id
                        FROM notas_cobro_extra nce
                        JOIN notas_entrada ne ON nce.nota_entrada_id = ne.id
                        JOIN rentas r ON ne.renta_id = r.id
                        WHERE nce.id = %s
                    """, (movimiento['referencia_id'],))
                elif movimiento['referencia_tabla'] == 'notas_cobro_retraso':
                    cursor.execute("""
                        SELECT ncr.id, 'retraso' as tipo, ncr.total as monto, ne.folio, r.id as renta_id
                        FROM notas_cobro_retraso ncr
                        JOIN notas_entrada ne ON ncr.nota_entrada_id = ne.id
                        JOIN rentas r ON ne.renta_id = r.id
                        WHERE ncr.id = %s
                    """, (movimiento['referencia_id'],))
                
                referencia_info = cursor.fetchone()
            except Exception as e:
                print(f"Error al obtener información de referencia: {e}")
        
        cursor.close()
        conn.close()
        
        # Formatear datos
        movimiento['fecha_formateada'] = movimiento['fecha'].strftime('%d/%m/%Y')
        movimiento['hora_formateada'] = movimiento['hora'].strftime('%H:%M:%S')
        movimiento['monto_formateado'] = f"{float(movimiento['monto']):,.2f}"
        
        return jsonify({
            'success': True,
            'movimiento': movimiento,
            'referencia_info': referencia_info
        })
        
    except Exception as e:
        print(f"Error al obtener detalle del movimiento: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@caja_bp.route('/api/ingresos-digitales')
def obtener_ingresos_digitales():
    """Obtiene ingresos por transferencia y tarjetas (NO son movimientos de caja)"""
    try:
        fecha_inicio = request.args.get('fecha_inicio', date.today().strftime('%Y-%m-%d'))
        fecha_fin = request.args.get('fecha_fin', fecha_inicio)
        sucursal_id = session.get('sucursal_id', 1)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Consultar prefacturas pagadas con métodos digitales
        cursor.execute("""
            SELECT 
                'Prefactura' as tipo_documento,
                p.id as documento_id,
                p.folio,
                p.fecha_creacion as fecha,
                p.metodo_pago,
                p.monto,
                p.numero_seguimiento,
                CONCAT(c.nombre, ' ', c.apellido1) as cliente_nombre,
                CONCAT(u.nombre, ' ', u.apellido1) as usuario_nombre
            FROM prefacturas p
            JOIN rentas r ON p.renta_id = r.id
            JOIN clientes c ON r.cliente_id = c.id
            LEFT JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.metodo_pago IN ('T.DÉBITO', 'T.CRÉDITO', 'TRANSFERENCIA')
            AND DATE(p.fecha_creacion) BETWEEN %s AND %s
            AND r.sucursal_id = %s
            
            UNION ALL
            
            SELECT 
                'Cobro Extra' as tipo_documento,
                nce.id as documento_id,
                CONCAT('CE-', nce.id) as folio,
                nce.fecha_creacion as fecha,
                nce.metodo_pago,
                nce.total as monto,
                nce.numero_seguimiento,
                CONCAT(c.nombre, ' ', c.apellido1) as cliente_nombre,
                CONCAT(u.nombre, ' ', u.apellido1) as usuario_nombre
            FROM notas_cobro_extra nce
            JOIN notas_entrada ne ON nce.nota_entrada_id = ne.id
            JOIN rentas r ON ne.renta_id = r.id
            JOIN clientes c ON r.cliente_id = c.id
            LEFT JOIN usuarios u ON nce.usuario_id = u.id
            WHERE nce.metodo_pago IN ('T.DÉBITO', 'T.CRÉDITO', 'TRANSFERENCIA')
            AND DATE(nce.fecha_creacion) BETWEEN %s AND %s
            AND r.sucursal_id = %s
            
            UNION ALL
            
            SELECT 
                'Cobro Retraso' as tipo_documento,
                ncr.id as documento_id,
                CONCAT('CR-', ncr.id) as folio,
                ncr.fecha_creacion as fecha,
                ncr.metodo_pago,
                ncr.total as monto,
                ncr.numero_seguimiento,
                CONCAT(c.nombre, ' ', c.apellido1) as cliente_nombre,
                CONCAT(u.nombre, ' ', u.apellido1) as usuario_nombre
            FROM notas_cobro_retraso ncr
            JOIN notas_entrada ne ON ncr.nota_entrada_id = ne.id
            JOIN rentas r ON ne.renta_id = r.id
            JOIN clientes c ON r.cliente_id = c.id
            LEFT JOIN usuarios u ON ncr.usuario_id = u.id
            WHERE ncr.metodo_pago IN ('T.DÉBITO', 'T.CRÉDITO', 'TRANSFERENCIA')
            AND DATE(ncr.fecha_creacion) BETWEEN %s AND %s
            AND r.sucursal_id = %s
            
            ORDER BY fecha DESC
        """, (
            fecha_inicio, fecha_fin, sucursal_id,
            fecha_inicio, fecha_fin, sucursal_id,
            fecha_inicio, fecha_fin, sucursal_id
        ))
        
        ingresos_digitales = cursor.fetchall()
        
        # Calcular totales por método de pago
        cursor.execute("""
            SELECT metodo_pago, SUM(total_monto) as total, COUNT(*) as cantidad
            FROM (
                SELECT metodo_pago, monto as total_monto
                FROM prefacturas p
                JOIN rentas r ON p.renta_id = r.id
                WHERE p.metodo_pago IN ('T.DÉBITO', 'T.CRÉDITO', 'TRANSFERENCIA')
                AND DATE(p.fecha_creacion) BETWEEN %s AND %s
                AND r.sucursal_id = %s
                
                UNION ALL
                
                SELECT metodo_pago, total as total_monto
                FROM notas_cobro_extra nce
                JOIN notas_entrada ne ON nce.nota_entrada_id = ne.id
                JOIN rentas r ON ne.renta_id = r.id
                WHERE nce.metodo_pago IN ('T.DÉBITO', 'T.CRÉDITO', 'TRANSFERENCIA')
                AND DATE(nce.fecha_creacion) BETWEEN %s AND %s
                AND r.sucursal_id = %s
                
                UNION ALL
                
                SELECT metodo_pago, total as total_monto
                FROM notas_cobro_retraso ncr
                JOIN notas_entrada ne ON ncr.nota_entrada_id = ne.id
                JOIN rentas r ON ne.renta_id = r.id
                WHERE ncr.metodo_pago IN ('T.DÉBITO', 'T.CRÉDITO', 'TRANSFERENCIA')
                AND DATE(ncr.fecha_creacion) BETWEEN %s AND %s
                AND r.sucursal_id = %s
            ) as todos_ingresos
            GROUP BY metodo_pago
        """, (
            fecha_inicio, fecha_fin, sucursal_id,
            fecha_inicio, fecha_fin, sucursal_id,
            fecha_inicio, fecha_fin, sucursal_id
        ))
        
        resumen_digital = cursor.fetchall()
        
        # Formatear datos
        for ingreso in ingresos_digitales:
            ingreso['fecha_formateada'] = ingreso['fecha'].strftime('%d/%m/%Y')
            ingreso['monto_formateado'] = f"{float(ingreso['monto']):,.2f}"
            
        for resumen in resumen_digital:
            resumen['total_formateado'] = f"{float(resumen['total']):,.2f}"
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ingresos_digitales': ingresos_digitales,
            'resumen_digital': resumen_digital,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        })
        
    except Exception as e:
        print(f"Error al obtener ingresos digitales: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500