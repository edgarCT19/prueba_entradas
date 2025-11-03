from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from utils.db import get_db_connection
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



bp_inventario = Blueprint('inventario', __name__, url_prefix='/inventario')

def obtener_siguiente_folio_nota_sucursal(cursor, sucursal_id):
    """
    Obtiene el siguiente folio consecutivo para notas (entrada y salida) de una sucursal específica
    Incluye tanto notas de rentas como notas de transferencias
    """
    # Considerar notas vinculadas a rentas Y folios de transferencias para determinar el siguiente folio
    cursor.execute("""
        SELECT IFNULL(MAX(folio), 0) + 1 AS siguiente_folio
        FROM (
            SELECT ne.folio 
            FROM notas_entrada ne
            JOIN rentas r ON ne.renta_id = r.id
            WHERE r.id_sucursal = %s
            UNION ALL
            SELECT ns.folio 
            FROM notas_salida ns
            JOIN rentas r ON ns.renta_id = r.id
            WHERE r.id_sucursal = %s
            UNION ALL
            SELECT CAST(mi.folio_nota_salida AS UNSIGNED) as folio
            FROM movimientos_inventario mi
            WHERE mi.id_sucursal = %s 
            AND mi.folio_nota_salida IS NOT NULL
            AND mi.folio_nota_salida != ''
            AND mi.tipo_movimiento = 'transferencia_salida'
            UNION ALL
            SELECT CAST(mi.folio_nota_entrada AS UNSIGNED) as folio
            FROM movimientos_inventario mi
            WHERE mi.id_sucursal = %s 
            AND mi.folio_nota_entrada IS NOT NULL
            AND mi.folio_nota_entrada != ''
            AND mi.tipo_movimiento = 'transferencia_entrada'
        ) AS todos_folios_sucursal
    """, (sucursal_id, sucursal_id, sucursal_id, sucursal_id))

    resultado = cursor.fetchone()
    return resultado['siguiente_folio'] if resultado and resultado.get('siguiente_folio') else 1

@bp_inventario.route('/general')
@requiere_permiso('ver_inventario_general')
def inventario_general():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre FROM sucursales")
    sucursales = cursor.fetchall()
    cursor.execute("""
        SELECT p.id_pieza, p.codigo_pieza, p.nombre_pieza, p.categoria, p.descripcion,
               SUM(i.total) AS total_empresa
        FROM piezas p
        LEFT JOIN inventario_sucursal i ON p.id_pieza = i.id_pieza
        GROUP BY p.id_pieza, p.codigo_pieza, p.nombre_pieza, p.categoria, p.descripcion
    """)
    piezas = cursor.fetchall()
    for pieza in piezas:
        pieza['sucursales'] = {}
        for suc in sucursales:
            cursor.execute("""
                SELECT total, disponibles, rentadas, daniadas, en_reparacion
                FROM inventario_sucursal
                WHERE id_pieza=%s AND id_sucursal=%s
            """, (pieza['id_pieza'], suc['id']))
            datos = cursor.fetchone() or {'total': 0, 'disponibles': 0, 'rentadas': 0, 'daniadas': 0, 'en_reparacion': 0}
            pieza['sucursales'][suc['id']] = datos
    cursor.close()
    conn.close()
    return render_template('inventario/inventario_general.html', piezas=piezas, sucursales=sucursales)



@bp_inventario.route('/agregar_pieza_general', methods=['POST'])
@requiere_permiso('agregar_pieza_inventario_general')
def agregar_pieza_general():
    nombre_pieza = request.form['nombre_pieza']
    codigo_pieza = request.form['codigo_pieza']
    categoria = request.form.get('categoria', '')
    descripcion = request.form.get('descripcion', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_pieza FROM piezas WHERE codigo_pieza=%s", (codigo_pieza,))
    existe = cursor.fetchone()
    if existe:
        # Trae los datos para la tabla
        cursor.execute("SELECT id, nombre FROM sucursales")
        sucursales = cursor.fetchall()
        cursor.execute("""
            SELECT p.id_pieza, p.codigo_pieza, p.nombre_pieza, p.categoria, p.descripcion,
                   SUM(i.total) AS total_empresa
            FROM piezas p
            LEFT JOIN inventario_sucursal i ON p.id_pieza = i.id_pieza
            GROUP BY p.id_pieza, p.codigo_pieza, p.nombre_pieza, p.categoria, p.descripcion
        """)
        piezas = cursor.fetchall()
        for pieza in piezas:
            pieza['sucursales'] = {}
            for suc in sucursales:
                cursor.execute("""
                    SELECT total, disponibles, rentadas, daniadas, en_reparacion
                    FROM inventario_sucursal
                    WHERE id_pieza=%s AND id_sucursal=%s
                """, (pieza['id_pieza'], suc['id']))
                datos = cursor.fetchone() or {'total': 0, 'disponibles': 0, 'rentadas': 0, 'daniadas': 0, 'en_reparacion': 0}
                pieza['sucursales'][suc['id']] = datos
        cursor.close()
        conn.close()
        # Renderiza la vista con el modal abierto y los datos previos
        return render_template(
            'inventario/inventario_general.html',
            piezas=piezas,
            sucursales=sucursales,
            show_modal_nueva_pieza=True,
            error_codigo='El código ingresado ya existe. Por favor ingresa uno diferente.',
            form_data={
                'nombre_pieza': nombre_pieza,
                'codigo_pieza': codigo_pieza,
                'categoria': categoria,
                'descripcion': descripcion
            }
        )
    # Si no existe, inserta normalmente
    cursor.execute(
        "INSERT INTO piezas (codigo_pieza, nombre_pieza, categoria, descripcion) VALUES (%s, %s, %s, %s)",
        (codigo_pieza, nombre_pieza, categoria, descripcion)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('inventario.inventario_general'))



@bp_inventario.route('/editar_pieza/<int:id_pieza>', methods=['POST'])
@requiere_permiso('modificar_existencias_inventario_general')
def editar_pieza(id_pieza):
    nombre_pieza = request.form['nombre_pieza']
    codigo_pieza = request.form['codigo_pieza']
    categoria = request.form.get('categoria', '')
    descripcion = request.form.get('descripcion', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Verifica si ya existe el código en otra pieza
    cursor.execute("SELECT id_pieza FROM piezas WHERE codigo_pieza=%s AND id_pieza!=%s", (codigo_pieza, id_pieza))
    existe = cursor.fetchone()
    if existe:
        # Trae los datos para la tabla
        cursor.execute("SELECT id, nombre FROM sucursales")
        sucursales = cursor.fetchall()
        cursor.execute("""
            SELECT p.id_pieza, p.codigo_pieza, p.nombre_pieza, p.categoria, p.descripcion,
                   SUM(i.total) AS total_empresa
            FROM piezas p
            LEFT JOIN inventario_sucursal i ON p.id_pieza = i.id_pieza
            GROUP BY p.id_pieza, p.codigo_pieza, p.nombre_pieza, p.categoria, p.descripcion
        """)
        piezas = cursor.fetchall()
        for pieza in piezas:
            pieza['sucursales'] = {}
            for suc in sucursales:
                cursor.execute("""
                    SELECT total, disponibles, rentadas, daniadas, en_reparacion
                    FROM inventario_sucursal
                    WHERE id_pieza=%s AND id_sucursal=%s
                """, (pieza['id_pieza'], suc['id']))
                datos = cursor.fetchone() or {'total': 0, 'disponibles': 0, 'rentadas': 0, 'daniadas': 0, 'en_reparacion': 0}
                pieza['sucursales'][suc['id']] = datos
        cursor.close()
        conn.close()
        # Renderiza la vista con el modal de editar abierto y los datos previos
        return render_template(
            'inventario/inventario_general.html',
            piezas=piezas,
            sucursales=sucursales,
            show_modal_editar_pieza=id_pieza,
            error_codigo_editar='El código ingresado ya existe en otra pieza. Por favor ingresa uno diferente.',
            form_data_editar={
                'nombre_pieza': nombre_pieza,
                'codigo_pieza': codigo_pieza,
                'categoria': categoria,
                'descripcion': descripcion
            }
        )
    # Si no existe, actualiza normalmente
    cursor.execute(
        "UPDATE piezas SET codigo_pieza=%s, nombre_pieza=%s, categoria=%s, descripcion=%s WHERE id_pieza=%s",
        (codigo_pieza, nombre_pieza, categoria, descripcion, id_pieza)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('inventario.inventario_general'))



from flask import session

# ...existing code...

@bp_inventario.route('/alta_baja_pieza', methods=['POST'])
@requiere_permiso('modificar_existencias_inventario_general')
def alta_baja_pieza():
    id_pieza = request.form['id_pieza']
    id_sucursal = request.form['id_sucursal']
    cantidad = int(request.form['cantidad'])
    tipo = request.form['tipo']
    descripcion = request.form.get('descripcion', '') if tipo == 'baja' else None
    usuario_id = session.get('user_id')  # <-- Obtén el usuario de la sesión

    conn = get_db_connection()
    cursor = conn.cursor()
    # Verifica si ya existe registro
    cursor.execute("SELECT total FROM inventario_sucursal WHERE id_pieza=%s AND id_sucursal=%s", (id_pieza, id_sucursal))
    row = cursor.fetchone()
    if row:
        if tipo == 'alta':
            cursor.execute("""
                UPDATE inventario_sucursal 
                SET total=total+%s, disponibles=disponibles+%s 
                WHERE id_pieza=%s AND id_sucursal=%s
            """, (cantidad, cantidad, id_pieza, id_sucursal))
        elif tipo == 'baja':
            cursor.execute("""
                UPDATE inventario_sucursal 
                SET total=GREATEST(total-%s,0), disponibles=GREATEST(disponibles-%s,0) 
                WHERE id_pieza=%s AND id_sucursal=%s
            """, (cantidad, cantidad, id_pieza, id_sucursal))
    else:
        if tipo == 'alta':
            cursor.execute("""
                INSERT INTO inventario_sucursal 
                (id_pieza, id_sucursal, total, disponibles, rentadas, daniadas, en_reparacion) 
                VALUES (%s, %s, %s, %s, 0, 0, 0)
            """, (id_pieza, id_sucursal, cantidad, cantidad))
    # Registrar movimiento para reporte (ahora incluye usuario)
    cursor.execute("""
        INSERT INTO movimientos_inventario (id_pieza, id_sucursal, tipo_movimiento, cantidad, descripcion, usuario)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (id_pieza, id_sucursal, tipo, cantidad, descripcion, usuario_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('inventario.inventario_general'))


@bp_inventario.route('/transferir_pieza', methods=['POST'])
@requiere_permiso('transferir_piezas_inventario')
def transferir_pieza():
    id_pieza = request.form['id_pieza']
    id_sucursal_origen = request.form['id_sucursal_origen']
    id_sucursal_destino = request.form['id_sucursal_destino']
    cantidad = int(request.form['cantidad'])
    usuario_id = session.get('user_id')  # <-- Obtén el usuario de la sesión

    conn = get_db_connection()
    cursor = conn.cursor()
    # Resta en origen
    cursor.execute("""
        UPDATE inventario_sucursal 
        SET total=GREATEST(total-%s,0), disponibles=GREATEST(disponibles-%s,0) 
        WHERE id_pieza=%s AND id_sucursal=%s
    """, (cantidad, cantidad, id_pieza, id_sucursal_origen))
    # Suma en destino (o crea si no existe)
    cursor.execute("SELECT total FROM inventario_sucursal WHERE id_pieza=%s AND id_sucursal=%s", (id_pieza, id_sucursal_destino))
    row = cursor.fetchone()
    if row:
        cursor.execute("""
            UPDATE inventario_sucursal 
            SET total=total+%s, disponibles=disponibles+%s 
            WHERE id_pieza=%s AND id_sucursal=%s
        """, (cantidad, cantidad, id_pieza, id_sucursal_destino))
    else:
        cursor.execute("""
            INSERT INTO inventario_sucursal 
            (id_pieza, id_sucursal, total, disponibles, rentadas, daniadas, en_reparacion) 
            VALUES (%s, %s, %s, %s, 0, 0, 0)
        """, (id_pieza, id_sucursal_destino, cantidad, cantidad))
    # Registrar movimiento de transferencia (ahora incluye usuario)
    cursor.execute("""
        INSERT INTO movimientos_inventario (id_pieza, id_sucursal, tipo_movimiento, cantidad, descripcion, usuario)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (id_pieza, id_sucursal_origen, 'transferencia_salida', cantidad, f'Transferencia a sucursal {id_sucursal_destino}', usuario_id))
    cursor.execute("""
        INSERT INTO movimientos_inventario (id_pieza, id_sucursal, tipo_movimiento, cantidad, descripcion, usuario)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (id_pieza, id_sucursal_destino, 'transferencia_entrada', cantidad, f'Transferencia desde sucursal {id_sucursal_origen}', usuario_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('inventario.inventario_general'))


##################################
############################# INVENTARIO MATRIZ
####################################




@bp_inventario.route('/sucursal/<int:sucursal_id>')
@requiere_permiso('ver_inventario_sucursal')
def inventario_sucursal(sucursal_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verificar que la sucursal existe
    cursor.execute("SELECT id as id_sucursal, nombre FROM sucursales WHERE id = %s", (sucursal_id,))
    sucursal = cursor.fetchone()
    
    if not sucursal:
        flash('Sucursal no encontrada', 'error')
        return redirect(url_for('inventario.inventario_general'))
    
    # Obtener piezas con inventario de esta sucursal específica
    cursor.execute("""
        SELECT p.id_pieza, p.nombre_pieza, p.categoria, 
               IFNULL(i.total, 0) AS total, 
               IFNULL(i.disponibles, 0) AS disponibles, 
               IFNULL(i.rentadas, 0) AS rentadas, 
               IFNULL(i.daniadas, 0) AS daniadas, 
               IFNULL(i.en_reparacion, 0) AS en_reparacion, 
               IFNULL(i.stock_minimo, 0) AS stock_minimo
        FROM piezas p
        LEFT JOIN inventario_sucursal i ON p.id_pieza = i.id_pieza AND i.id_sucursal = %s
        ORDER BY p.nombre_pieza
    """, (sucursal_id,))
    
    piezas = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('inventario/inventario_sucursal.html', piezas=piezas, sucursal=sucursal)















@bp_inventario.route('/enviar-equipos', methods=['POST'])
# @requiere_permiso('transferir_piezas_inventario')  # Temporalmente deshabilitado para prueba
def enviar_equipos():
    """
    Maneja el ENVÍO de equipos - Solo genera nota de salida y resta inventario origen
    """
    try:
        data = request.get_json()
        sucursal_origen_id = data.get('sucursal_origen_id')
        sucursal_destino_id = data.get('sucursal_destino_id')
        piezas = data.get('piezas', [])
        observaciones = data.get('observaciones', '')

        if not sucursal_origen_id or not sucursal_destino_id:
            return jsonify({'success': False, 'error': 'Faltan sucursales origen o destino'})

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # 1. Generar folio de SALIDA según sucursal origen
            folio_salida_num = obtener_siguiente_folio_nota_sucursal(cursor, sucursal_origen_id)
            folio_salida = str(folio_salida_num).zfill(5)

            # 2. Obtener nombres de sucursales
            cursor.execute("SELECT nombre FROM sucursales WHERE id = %s", (sucursal_origen_id,))
            nombre_origen = cursor.fetchone()['nombre']
            cursor.execute("SELECT nombre FROM sucursales WHERE id = %s", (sucursal_destino_id,))
            nombre_destino = cursor.fetchone()['nombre']

            # 3. Procesar cada pieza (SIN crear nota de salida)
            piezas_enviadas = 0
            usuario_id = session.get('user_id', 1)

            for pieza in piezas:
                id_pieza = pieza.get('id_pieza')
                cantidad = pieza.get('cantidad', 0)

                if cantidad <= 0:
                    continue

                # Verificar disponibilidad en origen
                cursor.execute("""
                    SELECT disponibles FROM inventario_sucursal 
                    WHERE id_pieza = %s AND id_sucursal = %s
                """, (id_pieza, sucursal_origen_id))
                
                row = cursor.fetchone()
                if not row or row['disponibles'] < cantidad:
                    continue

                # SOLO actualizar inventario origen (RESTA)
                cursor.execute("""
                    UPDATE inventario_sucursal 
                    SET disponibles = disponibles - %s, total = total - %s
                    WHERE id_sucursal = %s AND id_pieza = %s
                """, (cantidad, cantidad, sucursal_origen_id, id_pieza))

                # Registrar movimiento de SALIDA
                cursor.execute("""
                    INSERT INTO movimientos_inventario (
                        id_sucursal, id_pieza, tipo_movimiento, cantidad, fecha,
                        usuario, sucursal_destino, observaciones, descripcion,
                        folio_nota_salida
                    ) VALUES (%s, %s, 'transferencia_salida', %s, NOW(),
                             %s, %s, %s, %s, %s)
                """, (sucursal_origen_id, id_pieza, cantidad, 
                      usuario_id, sucursal_destino_id, observaciones,
                      f'Envío a {nombre_destino}', folio_salida))

                piezas_enviadas += 1

            conn.commit()

            if piezas_enviadas > 0:
                return jsonify({
                    'success': True,
                    'message': f'Equipos enviados correctamente a {nombre_destino}',
                    'folio_salida': folio_salida,
                    'piezas_enviadas': piezas_enviadas
                })
            else:
                return jsonify({'success': False, 'error': 'No se pudo enviar ninguna pieza'})

        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)})
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error en el procesamiento: {str(e)}'})


@bp_inventario.route('/recibir-equipos', methods=['POST'])
# @requiere_permiso('transferir_piezas_inventario')  # Temporalmente deshabilitado para prueba
def recibir_equipos():
    """
    Maneja la RECEPCIÓN de equipos - Solo genera nota de entrada y suma inventario destino
    """
    try:
        data = request.get_json()
        sucursal_origen_id = data.get('sucursal_origen_id')
        sucursal_destino_id = data.get('sucursal_destino_id')
        piezas = data.get('piezas', [])
        observaciones = data.get('observaciones', '')

        if not sucursal_origen_id or not sucursal_destino_id:
            return jsonify({'success': False, 'error': 'Faltan sucursales origen o destino'})

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # 1. Generar folio de ENTRADA según sucursal destino
            folio_entrada_num = obtener_siguiente_folio_nota_sucursal(cursor, sucursal_destino_id)
            folio_entrada = str(folio_entrada_num).zfill(5)

            # 2. Obtener nombres de sucursales
            cursor.execute("SELECT nombre FROM sucursales WHERE id = %s", (sucursal_origen_id,))
            nombre_origen = cursor.fetchone()['nombre']
            cursor.execute("SELECT nombre FROM sucursales WHERE id = %s", (sucursal_destino_id,))
            nombre_destino = cursor.fetchone()['nombre']

            # 3. Procesar cada pieza (SIN crear nota de entrada)
            piezas_recibidas = 0
            usuario_id = session.get('user_id', 1)

            for pieza in piezas:
                id_pieza = pieza.get('id_pieza')
                cantidad = pieza.get('cantidad', 0)

                if cantidad <= 0:
                    continue

                # SOLO actualizar inventario destino (SUMA)
                cursor.execute("""
                    INSERT INTO inventario_sucursal (id_sucursal, id_pieza, disponibles, total)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    disponibles = disponibles + VALUES(disponibles),
                    total = total + VALUES(total)
                """, (sucursal_destino_id, id_pieza, cantidad, cantidad))

                # Registrar movimiento de ENTRADA
                cursor.execute("""
                    INSERT INTO movimientos_inventario (
                        id_sucursal, id_pieza, tipo_movimiento, cantidad, fecha,
                        usuario, sucursal_destino, observaciones, descripcion,
                        folio_nota_entrada
                    ) VALUES (%s, %s, 'transferencia_entrada', %s, NOW(),
                             %s, %s, %s, %s, %s)
                """, (sucursal_destino_id, id_pieza, cantidad, 
                      usuario_id, sucursal_destino_id, observaciones,
                      f'Recepción de {nombre_origen}', folio_entrada))

                piezas_recibidas += 1

            conn.commit()

            if piezas_recibidas > 0:
                return jsonify({
                    'success': True,
                    'message': f'Equipos recibidos correctamente de {nombre_origen}',
                    'folio_entrada': folio_entrada,
                    'piezas_recibidas': piezas_recibidas
                })
            else:
                return jsonify({'success': False, 'error': 'No se pudo recibir ninguna pieza'})

        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)})
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error en el procesamiento: {str(e)}'})


@bp_inventario.route('/transferir-piezas-multiple', methods=['POST'])
@requiere_permiso('transferir_piezas_inventario')
def transferir_piezas_multiple():
    try:
        data = request.get_json()
        sucursal_origen_id = data.get('sucursal_origen_id')
        sucursal_destino_id = data.get('sucursal_destino_id')
        piezas = data.get('piezas', [])
        observaciones = data.get('observaciones', '')

        if not sucursal_origen_id or not sucursal_destino_id:
            return jsonify({'success': False, 'error': 'Faltan sucursales origen o destino'})

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # 1. Generar folios consecutivos por sucursal
            # Folio de SALIDA según sucursal origen
            folio_salida_num = obtener_siguiente_folio_nota_sucursal(cursor, sucursal_origen_id)
            folio_salida = str(folio_salida_num).zfill(5)
            
            # Folio de ENTRADA según sucursal destino
            folio_entrada_num = obtener_siguiente_folio_nota_sucursal(cursor, sucursal_destino_id)
            folio_entrada = str(folio_entrada_num).zfill(5)

            # 2. Obtener nombres de sucursales para las observaciones
            cursor.execute("SELECT nombre FROM sucursales WHERE id = %s", (sucursal_origen_id,))
            nombre_origen = cursor.fetchone()['nombre']
            cursor.execute("SELECT nombre FROM sucursales WHERE id = %s", (sucursal_destino_id,))
            nombre_destino = cursor.fetchone()['nombre']

            # 3. Crear nota de SALIDA (renta_id = NULL para transferencias)
            cursor.execute("""
                INSERT INTO notas_salida (
                    folio, renta_id, fecha, numero_referencia, observaciones
                ) VALUES (%s, NULL, NOW(), %s, %s)
            """, (folio_salida, f'TRANSFERENCIA-{folio_salida}', 
                  f'Transferencia de {nombre_origen} a {nombre_destino}. {observaciones}'))
            nota_salida_id = cursor.lastrowid

            # 4. Crear nota de ENTRADA (renta_id = NULL para transferencias)
            cursor.execute("""
                INSERT INTO notas_entrada (
                    folio, renta_id, nota_salida_id, fecha_entrada_real,
                    requiere_traslado_extra, costo_traslado_extra, observaciones,
                    estado, created_at, estado_retraso, accion_devolucion
                ) VALUES (%s, NULL, %s, NOW(), 'ninguno', 0, %s, 'normal', NOW(), 'Sin Retraso', 'no')
            """, (folio_entrada, nota_salida_id, 
                  f'Transferencia de {nombre_origen} a {nombre_destino}. {observaciones}'))
            nota_entrada_id = cursor.lastrowid

            # 5. Procesar cada pieza
            transferencias_exitosas = 0
            usuario_id = session.get('user_id', 1)

            for pieza in piezas:
                id_pieza = pieza.get('id_pieza')
                cantidad = pieza.get('cantidad', 0)

                if cantidad <= 0:
                    continue

                # Verificar disponibilidad en origen
                cursor.execute("""
                    SELECT disponibles FROM inventario_sucursal 
                    WHERE id_pieza = %s AND id_sucursal = %s
                """, (id_pieza, sucursal_origen_id))
                
                row = cursor.fetchone()
                if not row or row['disponibles'] < cantidad:
                    continue  # Saltar si no hay suficiente stock

                # Crear detalles de las notas
                cursor.execute("""
                    INSERT INTO notas_salida_detalle (nota_salida_id, id_pieza, cantidad)
                    VALUES (%s, %s, %s)
                """, (nota_salida_id, id_pieza, cantidad))

                cursor.execute("""
                    INSERT INTO notas_entrada_detalle (
                        nota_entrada_id, id_pieza, cantidad_esperada, cantidad_recibida,
                        cantidad_buena, cantidad_danada, cantidad_sucia, cantidad_perdida
                    ) VALUES (%s, %s, %s, %s, %s, 0, 0, 0)
                """, (nota_entrada_id, id_pieza, cantidad, cantidad, cantidad))

                # Actualizar inventario origen (RESTA)
                cursor.execute("""
                    UPDATE inventario_sucursal 
                    SET disponibles = disponibles - %s, total = total - %s
                    WHERE id_sucursal = %s AND id_pieza = %s
                """, (cantidad, cantidad, sucursal_origen_id, id_pieza))

                # Actualizar/crear inventario destino (SUMA)
                cursor.execute("""
                    INSERT INTO inventario_sucursal (id_sucursal, id_pieza, disponibles, total)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    disponibles = disponibles + VALUES(disponibles),
                    total = total + VALUES(total)
                """, (sucursal_destino_id, id_pieza, cantidad, cantidad))

                # Registrar movimientos con folios
                cursor.execute("""
                    INSERT INTO movimientos_inventario (
                        id_sucursal, id_pieza, tipo_movimiento, cantidad, fecha,
                        usuario, sucursal_destino, observaciones, descripcion,
                        folio_nota_salida, folio_nota_entrada
                    ) VALUES (%s, %s, 'transferencia_salida', %s, NOW(),
                             %s, %s, %s, %s, %s, %s)
                """, (sucursal_origen_id, id_pieza, cantidad, 
                      usuario_id, sucursal_destino_id, observaciones,
                      f'Transferencia a {nombre_destino}',
                      folio_salida, folio_entrada))

                cursor.execute("""
                    INSERT INTO movimientos_inventario (
                        id_sucursal, id_pieza, tipo_movimiento, cantidad, fecha,
                        usuario, sucursal_destino, observaciones, descripcion,
                        folio_nota_salida, folio_nota_entrada
                    ) VALUES (%s, %s, 'transferencia_entrada', %s, NOW(),
                             %s, %s, %s, %s, %s, %s)
                """, (sucursal_destino_id, id_pieza, cantidad,
                      usuario_id, sucursal_origen_id, observaciones,
                      f'Transferencia desde {nombre_origen}',
                      folio_salida, folio_entrada))

                transferencias_exitosas += 1

            conn.commit()

            if transferencias_exitosas > 0:
                return jsonify({
                    'success': True,
                    'message': f'Transferencia completada exitosamente. {transferencias_exitosas} tipos de piezas transferidas.',
                    'folio_salida': folio_salida,
                    'folio_entrada': folio_entrada,
                    'nota_salida_id': nota_salida_id,  # <- AGREGAR ESTA LÍNEA
                    'transferencias_exitosas': transferencias_exitosas
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No se pudo realizar ninguna transferencia. Verifica el stock disponible.'
                })

        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)})
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error en el procesamiento: {str(e)}'})














@bp_inventario.route('/mandar_a_reparacion', methods=['POST'])
@requiere_permiso('mandar_pieza_reparacion')
def mandar_a_reparacion():
    id_pieza = request.form['id_pieza']
    id_sucursal = request.form['id_sucursal']
    cantidad = int(request.form['cantidad'])

    conn = get_db_connection()
    cursor = conn.cursor()
    # Restar de dañadas, sumar a en_reparacion
    cursor.execute("""
        UPDATE inventario_sucursal
        SET daniadas = GREATEST(daniadas - %s, 0),
            en_reparacion = en_reparacion + %s
        WHERE id_pieza = %s AND id_sucursal = %s
    """, (cantidad, cantidad, id_pieza, id_sucursal))
    
    usuario_id = session.get('user_id')
    cursor.execute("""
    INSERT INTO movimientos_inventario (id_pieza, id_sucursal, tipo_movimiento, cantidad, descripcion, usuario)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (id_pieza, id_sucursal, 'a_reparacion', cantidad, 'Enviado a reparación', usuario_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash(f'Se enviaron {cantidad} piezas a reparación exitosamente', 'success')
    
    
    return redirect(url_for('inventario.inventario_sucursal', sucursal_id=id_sucursal))







@bp_inventario.route('/regresar_a_disponible', methods=['POST'])
@requiere_permiso('regresar_pieza_disponible')
def regresar_a_disponible():
    id_pieza = request.form['id_pieza']
    id_sucursal = request.form['id_sucursal']
    cantidad = int(request.form['cantidad'])

    conn = get_db_connection()
    cursor = conn.cursor()
    # Restar de en_reparacion, sumar a disponibles
    cursor.execute("""
        UPDATE inventario_sucursal
        SET en_reparacion = GREATEST(en_reparacion - %s, 0),
            disponibles = disponibles + %s
        WHERE id_pieza = %s AND id_sucursal = %s
    """, (cantidad, cantidad, id_pieza, id_sucursal))
    
    usuario_id = session.get('user_id')
    cursor.execute("""
    INSERT INTO movimientos_inventario (id_pieza, id_sucursal, tipo_movimiento, cantidad, descripcion, usuario)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (id_pieza, id_sucursal, 'a_disponible', cantidad, 'Regresado a disponibles', usuario_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash(f'Se regresaron {cantidad} piezas a disponibles exitosamente', 'success')
    

    return redirect(url_for('inventario.inventario_sucursal', sucursal_id=id_sucursal))




















# Agregar esta nueva función al final del archivo inventario.py, antes de la última función

@bp_inventario.route('/pdf-transferencia-salida/<folio>')
@requiere_permiso('ver_inventario_sucursal')
def generar_pdf_transferencia_salida(folio):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    from flask import send_file
    from PyPDF2 import PdfReader, PdfWriter
    import os
    from datetime import datetime
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener datos de la transferencia de salida desde movimientos_inventario
        cursor.execute("""
            SELECT mi.*, p.nombre_pieza, p.categoria,
                   so.nombre AS sucursal_origen, sd.nombre AS sucursal_destino
            FROM movimientos_inventario mi
            JOIN piezas p ON mi.id_pieza = p.id_pieza
            JOIN sucursales so ON mi.id_sucursal = so.id
            LEFT JOIN sucursales sd ON mi.sucursal_destino = sd.id
            WHERE mi.folio_nota_salida = %s 
            AND mi.tipo_movimiento = 'transferencia_salida'
            ORDER BY p.nombre_pieza
        """, (folio,))
        
        movimientos = cursor.fetchall()
        
        if not movimientos:
            cursor.close()
            conn.close()
            return "Transferencia de salida no encontrada", 404
        
        # Datos generales de la transferencia
        primer_movimiento = movimientos[0]
        
        cursor.close()
        conn.close()
        
        # --- GENERAR PDF CON EL MISMO DISEÑO QUE NOTAS DE SALIDA ---
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Registrar fuente
        try:
            font_path = os.path.join(current_app.root_path, 'static/fonts/Carlito-Regular.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Carlito', font_path))
        except:
            pass
        
        # CONFIGURACIÓN INICIAL (igual que notas_salida)
        page_width, page_height = letter
        y_position = page_height - 100
        
        # Folio (esquina superior derecha)
        can.setFont("Carlito", 16)
        can.drawRightString(502, 670, f"#{folio}")
        
        # Fecha y hora de emisión
        can.setFont("Carlito", 10)
        fecha_emision = primer_movimiento['fecha'].strftime('%d/%m/%Y - %H:%M:%S')
        can.drawRightString(573, 708, f"{fecha_emision}")
        
        # === DATOS DE TRANSFERENCIA (en lugar de cliente) ===
        can.setFont("Carlito", 12)
        can.drawString(62, 703, "TRANSFERENCIA DE EQUIPOS")
        
        # Sucursal origen
        can.setFont("Carlito", 10)
        can.drawString(62, 687, f"DESDE: {primer_movimiento['sucursal_origen'].upper()}")
        
        # Sucursal destino
        can.drawString(62, 671, f"HACIA: {primer_movimiento['sucursal_destino'].upper()}")
        
        # Número de referencia (descripción)
        can.drawString(231, 671, f"REF: TRANSFERENCIA-{folio}")
        
        # DATOS DE PIEZAS (igual que notas_salida)
        y_position -= 85
        can.setFont("Carlito", 10)
        for movimiento in movimientos:
            # Verificar si necesitamos nueva página
            if y_position < 150:
                can.showPage()
                can.setFont("Carlito", 10)
                y_position = page_height - 60
            
            can.drawString(70, y_position + 5, str(movimiento['cantidad']))
            can.drawString(140, y_position + 5, movimiento['nombre_pieza'].upper())
            y_position -= 13
        
        y_position -= 5
        
        # Descripción de la transferencia
        can.setFont("Carlito", 10)
        can.drawString(60, y_position, f"MOTIVO: {primer_movimiento['descripcion']}")
        y_position -= 15
        
        # Observaciones si existen
        if primer_movimiento['observaciones']:
            can.drawString(60, y_position, f"OBSERVACIONES: {primer_movimiento['observaciones']}")
            y_position -= 15
        
        y_position -= 30
        
        # Línea separadora
        can.line(30, y_position + 24, page_width - 30, y_position + 24)
        y_position -= 35
        
        # === FIRMAS ===
        can.setFont("Carlito", 10)
        # Líneas para firmas
        can.line(60, y_position, 250, y_position)  # Línea origen
        can.line(350, y_position, 540, y_position)  # Línea destino
        y_position -= 15
        
        # Etiquetas de firmas
        can.drawString(60, y_position, f"ENTREGA: {primer_movimiento['sucursal_origen'].upper()}")
        can.drawString(350, y_position, f"RECIBE: {primer_movimiento['sucursal_destino'].upper()}")
        y_position -= 20
        
        can.drawString(60, y_position, "NOMBRE: ________________________")
        can.drawString(350, y_position, "NOMBRE: ________________________")
        y_position -= 15
        
        can.drawString(60, y_position, "FIRMA: __________________________")
        can.drawString(350, y_position, "FIRMA: __________________________")
        
        can.save()
        packet.seek(0)
        
        # --- COMBINAR CON LA PLANTILLA (igual que notas_salida) ---
        try:
            plantilla_path = os.path.join(current_app.root_path, 'static/notas/salida_plantilla.pdf')
            overlay_pdf = PdfReader(packet)
            output = PdfWriter()

            if os.path.exists(plantilla_path):
                plantilla_pdf = PdfReader(plantilla_path)
                # Primera página: plantilla + overlay
                page = plantilla_pdf.pages[0]
                page.merge_page(overlay_pdf.pages[0])
                output.add_page(page)
            else:
                # Si no hay plantilla, solo overlay
                for page in overlay_pdf.pages:
                    output.add_page(page)
        except Exception as e:
            print(f"Error con plantilla: {e}")
            overlay_pdf = PdfReader(packet)
            output = PdfWriter()
            for page in overlay_pdf.pages:
                output.add_page(page)

        output_stream = BytesIO()
        output.write(output_stream)
        output_stream.seek(0)
        
        return send_file(
            output_stream,
            download_name=f"nota_salida_transferencia_{folio}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return f"Error al generar PDF: {str(e)}", 500


@bp_inventario.route('/pdf-transferencia-entrada/<folio>')
@requiere_permiso('ver_inventario_sucursal')
def generar_pdf_transferencia_entrada(folio):
    """
    Genera PDF para transferencia de entrada desde movimientos_inventario
    Usa el mismo diseño que las notas de entrada de rentas
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    from flask import send_file
    from PyPDF2 import PdfReader, PdfWriter
    import os
    from datetime import datetime
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener datos de la transferencia de entrada desde movimientos_inventario
        cursor.execute("""
            SELECT mi.*, p.nombre_pieza, p.categoria,
                   so.nombre AS sucursal_origen, sd.nombre AS sucursal_destino
            FROM movimientos_inventario mi
            JOIN piezas p ON mi.id_pieza = p.id_pieza
            JOIN sucursales so ON mi.id_sucursal = so.id
            LEFT JOIN sucursales sd ON mi.sucursal_destino = sd.id
            WHERE mi.folio_nota_entrada = %s 
            AND mi.tipo_movimiento = 'transferencia_entrada'
            ORDER BY p.nombre_pieza
        """, (folio,))
        
        movimientos = cursor.fetchall()
        
        if not movimientos:
            cursor.close()
            conn.close()
            return "Transferencia de entrada no encontrada", 404
        
        # Datos generales de la transferencia
        primer_movimiento = movimientos[0]
        
        cursor.close()
        conn.close()
        
        # --- GENERAR PDF CON EL MISMO DISEÑO QUE NOTAS DE ENTRADA ---
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Registrar fuente
        try:
            font_path = os.path.join(current_app.root_path, 'static/fonts/Carlito-Regular.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Carlito', font_path))
        except:
            pass
        
        # Folio de Nota de Entrada
        can.setFont("Carlito", 9)
        texto = "FOLIO DE ENTRADA:"
        x = 450
        y = 670
        can.drawString(x, y, texto)
        
        # Dibuja el folio en tamaño 12, justo después del texto
        folio_str = f"#{folio}"
        can.setFont("Helvetica-Bold", 12)
        x_folio = x + can.stringWidth(texto, "Helvetica-Bold", 10) - 25
        can.drawString(x_folio, y, folio_str)
        
        # === DATOS DE TRANSFERENCIA (en lugar de cliente) ===
        can.setFont("Carlito", 12)
        can.drawString(63, 703, "RECEPCIÓN DE TRANSFERENCIA")
        
        # Fecha
        can.setFont("Helvetica", 10)
        fecha_formato = primer_movimiento['fecha'].strftime('%d/%m/%Y %H:%M')
        can.drawString(479, 708, f" {fecha_formato}")
        
        # Sucursal origen
        can.setFont("Helvetica", 10)
        can.drawString(67, 671, f"PROCEDENTE DE: {primer_movimiento['sucursal_origen'] or 'No especificado'}")
        
        # Sucursal destino
        can.setFont("Helvetica-Bold", 10)
        can.drawString(67, 657, f"RECIBIDO EN: {primer_movimiento['sucursal_destino']}")
        
        # === TABLA DE PIEZAS (igual que notas_entrada) ===
        y = 630
        can.setFont("Helvetica-Bold", 10)
        
        y -= 15
        can.setFont("Helvetica-Bold", 9)
        can.drawString(60, y, "Pieza")
        can.drawString(250, y, "Cantidad")
        can.drawString(300, y, "Recibidas")
        can.drawString(375, y, "Buenas")
        can.drawString(420, y, "Categoría")
        
        y -= 13
        can.setFont("Helvetica", 9)
        for movimiento in movimientos:
            if y < 100:
                can.showPage()
                y = 750
            
            can.drawString(60, y, f"{movimiento['nombre_pieza']}")
            can.drawString(250, y, str(movimiento['cantidad']))
            can.drawString(300, y, str(movimiento['cantidad']))  # Para transferencias, recibidas = cantidad
            can.drawString(375, y, str(movimiento['cantidad']))  # Para transferencias, buenas = cantidad
            can.drawString(420, y, movimiento['categoria'] or '-')
            y -= 13
        
        y -= 10
        can.setFont("Helvetica", 10)
        can.drawString(60, y, f"PROCEDENTE DE: {primer_movimiento['sucursal_origen'] or 'No especificado'}")
        y -= 13
        
        # Motivo de transferencia
        can.drawString(60, y, f"MOTIVO: {primer_movimiento['descripcion']}")
        y -= 13
        
        # === FIRMAS ===
        y -= 30
        can.setFont("Carlito", 10)
        # Línea para firma de recepción
        can.line(60, y, 250, y)
        # Línea para firma de entrega
        can.line(350, y, 540, y)
        
        y -= 15
        # Etiquetas de firmas
        can.drawString(60, y, f"RECIBE: {primer_movimiento['sucursal_destino'].upper()}")
        can.drawString(350, y, f"ENTREGA: {primer_movimiento['sucursal_origen'].upper()}")
        
        y -= 10
        can.setFont("Helvetica-Bold", 10)
        can.drawString(60, y, "Observaciones:")
        y -= 13
        can.setFont("Helvetica", 10)
        observaciones_texto = primer_movimiento['observaciones'] or "Transferencia de equipos entre sucursales"
        can.drawString(60, y, observaciones_texto)
        
        can.save()
        packet.seek(0)
        
        # --- COMBINAR CON LA PLANTILLA (igual que notas_entrada) ---
        try:
            plantilla_path = os.path.join(current_app.root_path, 'static/notas/Plantilla_entrada.pdf')
            if os.path.exists(plantilla_path):
                plantilla_pdf = PdfReader(plantilla_path)
                overlay_pdf = PdfReader(packet)
                output = PdfWriter()
                page = plantilla_pdf.pages[0]
                page.merge_page(overlay_pdf.pages[0])
                output.add_page(page)
            else:
                overlay_pdf = PdfReader(packet)
                output = PdfWriter()
                output.add_page(overlay_pdf.pages[0])
        except Exception as e:
            print(f"Error con plantilla: {e}")
            overlay_pdf = PdfReader(packet)
            output = PdfWriter()
            output.add_page(overlay_pdf.pages[0])
        
        output_stream = BytesIO()
        output.write(output_stream)
        output_stream.seek(0)
        
        return send_file(
            output_stream,
            download_name=f"nota_entrada_transferencia_{folio}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return f"Error al generar PDF: {str(e)}", 500


@bp_inventario.route('/pdf-nota-salida-transferencia/<int:nota_salida_id>')
@requiere_permiso('ver_inventario_sucursal')
def generar_pdf_nota_salida_transferencia(nota_salida_id):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    from flask import send_file
    import os
    from datetime import datetime
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener datos de la nota de salida (transferencia)
        cursor.execute("""
            SELECT ns.folio, ns.fecha, ns.numero_referencia, ns.observaciones,
                   so.nombre AS sucursal_origen, sd.nombre AS sucursal_destino
            FROM notas_salida ns
            LEFT JOIN sucursales so ON SUBSTRING_INDEX(ns.numero_referencia, ' ', -1) = so.id
            LEFT JOIN sucursales sd ON SUBSTRING_INDEX(SUBSTRING_INDEX(ns.numero_referencia, ' A ', -1), ' ', 1) = sd.id
            WHERE ns.id = %s AND ns.renta_id IS NULL
        """, (nota_salida_id,))
        nota = cursor.fetchone()
        
        if not nota:
            cursor.close()
            conn.close()
            return "Nota de transferencia no encontrada", 404
        
        # Extraer sucursales del numero_referencia de forma más robusta
        cursor.execute("""
            SELECT ns.folio, ns.fecha, ns.numero_referencia, ns.observaciones,
                   ne.sucursal_origen_id, ne.sucursal_destino_id,
                   so.nombre AS sucursal_origen, sd.nombre AS sucursal_destino
            FROM notas_salida ns
            LEFT JOIN notas_entrada ne ON ne.nota_salida_id = ns.id
            LEFT JOIN sucursales so ON ne.sucursal_origen_id = so.id
            LEFT JOIN sucursales sd ON ne.sucursal_destino_id = sd.id
            WHERE ns.id = %s AND ns.renta_id IS NULL
        """, (nota_salida_id,))
        nota = cursor.fetchone()
        
        # Si no hay datos de entrada, usar la información del query anterior
        if not nota or not nota['sucursal_origen']:
            cursor.execute("""
                SELECT ns.folio, ns.fecha, ns.numero_referencia, ns.observaciones
                FROM notas_salida ns
                WHERE ns.id = %s AND ns.renta_id IS NULL
            """, (nota_salida_id,))
            nota = cursor.fetchone()
            
            # Extraer info de sucursales del numero_referencia manualmente
            if nota and 'TRANSFERENCIA' in nota['numero_referencia']:
                # Buscar en movimientos_inventario para obtener las sucursales
                cursor.execute("""
                    SELECT DISTINCT mi.id_sucursal, mi.sucursal_destino, s1.nombre as origen, s2.nombre as destino
                    FROM movimientos_inventario mi
                    LEFT JOIN sucursales s1 ON mi.id_sucursal = s1.id
                    LEFT JOIN sucursales s2 ON mi.sucursal_destino = s2.id
                    WHERE mi.folio_nota_salida = %s
                    AND mi.tipo_movimiento = 'transferencia_salida'
                    LIMIT 1
                """, (nota['folio'],))
                sucursales_info = cursor.fetchone()
                
                if sucursales_info:
                    nota['sucursal_origen'] = sucursales_info['origen']
                    nota['sucursal_destino'] = sucursales_info['destino']
                else:
                    nota['sucursal_origen'] = 'No identificada'
                    nota['sucursal_destino'] = 'No identificada'
        
        # Obtener piezas de la nota de salida
        cursor.execute("""
            SELECT nsd.cantidad, p.nombre_pieza, p.categoria
            FROM notas_salida_detalle nsd
            JOIN piezas p ON nsd.id_pieza = p.id_pieza
            WHERE nsd.nota_salida_id = %s
            ORDER BY p.nombre_pieza
        """, (nota_salida_id,))
        piezas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Generar PDF
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Registrar fuente si existe
        try:
            font_path = os.path.join(current_app.root_path, 'static/fonts/Carlito-Regular.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Carlito', font_path))
                font_name = 'Carlito'
            else:
                font_name = 'Helvetica'
        except:
            font_name = 'Helvetica'
        
        # Configuración inicial
        page_width, page_height = letter
        y_position = page_height - 60
        
        # Encabezado
        can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 18)
        can.drawCentredText(page_width/2, y_position, "NOTA DE SALIDA - TRANSFERENCIA")
        y_position -= 40
        
        # Folio
        can.setFont(font_name, 14)
        can.drawRightString(page_width - 50, y_position, f"Folio: #{str(nota['folio']).zfill(5)}")
        y_position -= 30
        
        # Fecha
        can.setFont(font_name, 11)
        fecha_formato = nota['fecha'].strftime('%d/%m/%Y %H:%M') if nota['fecha'] else 'No disponible'
        can.drawString(50, y_position, f"Fecha: {fecha_formato}")
        y_position -= 25
        
        # Información de transferencia
        can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 12)
        can.drawString(50, y_position, "DETALLES DE TRANSFERENCIA:")
        y_position -= 20
        
        can.setFont(font_name, 11)
        can.drawString(70, y_position, f"Desde: {nota['sucursal_origen']}")
        y_position -= 15
        can.drawString(70, y_position, f"Hacia: {nota['sucursal_destino']}")
        y_position -= 15
        can.drawString(70, y_position, f"Referencia: {nota['numero_referencia']}")
        y_position -= 30
        
        # Tabla de piezas
        can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 12)
        can.drawString(50, y_position, "PIEZAS TRANSFERIDAS:")
        y_position -= 20
        
        # Encabezados de tabla
        can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 10)
        can.drawString(70, y_position, "CANTIDAD")
        can.drawString(150, y_position, "PIEZA")
        can.drawString(400, y_position, "CATEGORÍA")
        y_position -= 15
        
        # Línea separadora
        can.line(50, y_position, page_width - 50, y_position)
        y_position -= 10
        
        # Datos de piezas
        can.setFont(font_name, 10)
        total_piezas = 0
        for pieza in piezas:
            # Verificar si necesitamos nueva página
            if y_position < 100:
                can.showPage()
                can.setFont(font_name, 10)
                y_position = page_height - 60
            
            can.drawString(70, y_position, str(pieza['cantidad']))
            can.drawString(150, y_position, pieza['nombre_pieza'])
            can.drawString(400, y_position, pieza['categoria'] or '-')
            total_piezas += pieza['cantidad']
            y_position -= 15
        
        # Total
        y_position -= 10
        can.line(50, y_position, page_width - 50, y_position)
        y_position -= 15
        can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 11)
        can.drawString(70, y_position, f"TOTAL PIEZAS: {total_piezas}")
        y_position -= 30
        
        # Observaciones
        if nota['observaciones']:
            can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 11)
            can.drawString(50, y_position, "OBSERVACIONES:")
            y_position -= 15
            can.setFont(font_name, 10)
            can.drawString(50, y_position, nota['observaciones'])
            y_position -= 30
        
        # Firmas
        y_position -= 20
        can.setFont(font_name, 10)
        can.line(50, y_position, 250, y_position)  # Línea origen
        can.line(350, y_position, 550, y_position)  # Línea destino
        y_position -= 15
        can.drawString(50, y_position, f"ENTREGA: {nota['sucursal_origen']}")
        can.drawString(350, y_position, f"RECIBE: {nota['sucursal_destino']}")
        y_position -= 20
        can.drawString(50, y_position, "Nombre: _________________________")
        can.drawString(350, y_position, "Nombre: _________________________")
        y_position -= 15
        can.drawString(50, y_position, "Firma: __________________________")
        can.drawString(350, y_position, "Firma: __________________________")
        
        can.save()
        packet.seek(0)
        
        return send_file(
            packet,
            download_name=f"nota_salida_transferencia_{str(nota['folio']).zfill(5)}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return f"Error al generar PDF: {str(e)}", 500


@bp_inventario.route('/pdf-nota-entrada-transferencia/<int:nota_entrada_id>')
@requiere_permiso('ver_inventario_sucursal')
def generar_pdf_nota_entrada_transferencia(nota_entrada_id):
    """
    Genera PDF para nota de entrada de transferencia (recepción)
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    from flask import send_file
    import os
    from datetime import datetime
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener datos de la nota de entrada (recepción)
        cursor.execute("""
            SELECT ne.folio, ne.fecha_entrada_real, ne.observaciones
            FROM notas_entrada ne
            WHERE ne.id = %s AND ne.renta_id IS NULL
        """, (nota_entrada_id,))
        nota = cursor.fetchone()
        
        if not nota:
            cursor.close()
            conn.close()
            return "Nota de entrada no encontrada", 404
        
        # Obtener piezas de la nota de entrada
        cursor.execute("""
            SELECT ned.cantidad_recibida, p.nombre_pieza, p.categoria
            FROM notas_entrada_detalle ned
            JOIN piezas p ON ned.id_pieza = p.id_pieza
            WHERE ned.nota_entrada_id = %s
            ORDER BY p.nombre_pieza
        """, (nota_entrada_id,))
        piezas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Generar PDF
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Registrar fuente si existe
        try:
            font_path = os.path.join(current_app.root_path, 'static/fonts/Carlito-Regular.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Carlito', font_path))
                font_name = 'Carlito'
            else:
                font_name = 'Helvetica'
        except:
            font_name = 'Helvetica'
        
        # Configuración inicial
        page_width, page_height = letter
        y_position = page_height - 60
        
        # Encabezado
        can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 18)
        can.drawCentredText(page_width/2, y_position, "NOTA DE ENTRADA - RECEPCIÓN")
        y_position -= 40
        
        # Folio
        can.setFont(font_name, 14)
        can.drawRightString(page_width - 50, y_position, f"Folio: #{str(nota['folio']).zfill(5)}")
        y_position -= 30
        
        # Fecha
        can.setFont(font_name, 11)
        fecha_formato = nota['fecha_entrada_real'].strftime('%d/%m/%Y %H:%M') if nota['fecha_entrada_real'] else 'No disponible'
        can.drawString(50, y_position, f"Fecha de Recepción: {fecha_formato}")
        y_position -= 40
        
        # Tabla de piezas
        can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 12)
        can.drawString(50, y_position, "PIEZAS RECIBIDAS:")
        y_position -= 20
        
        # Encabezados de tabla
        can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 10)
        can.drawString(70, y_position, "CANTIDAD")
        can.drawString(150, y_position, "PIEZA")
        can.drawString(400, y_position, "CATEGORÍA")
        y_position -= 15
        
        # Línea separadora
        can.line(50, y_position, page_width - 50, y_position)
        y_position -= 10
        
        # Datos de piezas
        can.setFont(font_name, 10)
        total_piezas = 0
        for pieza in piezas:
            # Verificar si necesitamos nueva página
            if y_position < 100:
                can.showPage()
                y_position = page_height - 60
            
            can.drawString(70, y_position, str(pieza['cantidad_recibida']))
            can.drawString(150, y_position, pieza['nombre_pieza'])
            can.drawString(400, y_position, pieza['categoria'] or '-')
            total_piezas += pieza['cantidad_recibida']
            y_position -= 15
        
        # Total
        y_position -= 10
        can.line(50, y_position, page_width - 50, y_position)
        y_position -= 15
        can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 11)
        can.drawString(70, y_position, f"TOTAL PIEZAS RECIBIDAS: {total_piezas}")
        y_position -= 30
        
        # Observaciones
        if nota['observaciones']:
            can.setFont(font_name + '-Bold' if font_name == 'Helvetica' else font_name, 11)
            can.drawString(50, y_position, "OBSERVACIONES:")
            y_position -= 15
            can.setFont(font_name, 10)
            can.drawString(50, y_position, nota['observaciones'])
            y_position -= 30
        
        # Firma
        y_position -= 20
        can.setFont(font_name, 10)
        can.line(50, y_position, 300, y_position)
        y_position -= 15
        can.drawString(50, y_position, "RECIBIDO POR:")
        y_position -= 20
        can.drawString(50, y_position, "Nombre: _________________________")
        y_position -= 15
        can.drawString(50, y_position, "Firma: __________________________")
        y_position -= 15
        can.drawString(50, y_position, "Fecha: __________________________")
        
        can.save()
        packet.seek(0)
        
        return send_file(
            packet,
            download_name=f"nota_entrada_recepcion_{str(nota['folio']).zfill(5)}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return f"Error al generar PDF: {str(e)}", 500


# Funciones del historial de transferencias
@bp_inventario.route('/historial-transferencias/<int:sucursal_id>')
@requiere_permiso('ver_inventario_sucursal')
def historial_transferencias_sucursal(sucursal_id):
    """
    Obtiene el historial de transferencias (enviadas y recibidas) de una sucursal específica
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener transferencias ENVIADAS (salidas) de esta sucursal
        cursor.execute("""
            SELECT 
                'enviada' as tipo_transferencia,
                mi.folio_nota_salida as folio,
                mi.fecha,
                mi.observaciones,
                mi.descripcion,
                sd.nombre as sucursal_destino,
                NULL as sucursal_origen,
                COUNT(DISTINCT mi.id_pieza) as total_tipos_piezas,
                SUM(mi.cantidad) as total_cantidad
            FROM movimientos_inventario mi
            LEFT JOIN sucursales sd ON mi.sucursal_destino = sd.id
            WHERE mi.id_sucursal = %s 
            AND mi.tipo_movimiento = 'transferencia_salida'
            AND mi.folio_nota_salida IS NOT NULL
            GROUP BY mi.folio_nota_salida, mi.fecha, mi.observaciones, mi.descripcion, sd.nombre
            
            UNION ALL
            
            SELECT 
                'recibida' as tipo_transferencia,
                mi.folio_nota_entrada as folio,
                mi.fecha,
                mi.observaciones,
                mi.descripcion,
                NULL as sucursal_destino,
                so.nombre as sucursal_origen,
                COUNT(DISTINCT mi.id_pieza) as total_tipos_piezas,
                SUM(mi.cantidad) as total_cantidad
            FROM movimientos_inventario mi
            LEFT JOIN sucursales so ON mi.sucursal_destino = so.id
            WHERE mi.id_sucursal = %s 
            AND mi.tipo_movimiento = 'transferencia_entrada'
            AND mi.folio_nota_entrada IS NOT NULL
            GROUP BY mi.folio_nota_entrada, mi.fecha, mi.observaciones, mi.descripcion, so.nombre
            
            UNION ALL
            
            SELECT 
                'alta_equipo' as tipo_transferencia,
                mi.folio_nota_entrada as folio,
                mi.fecha,
                mi.observaciones,
                mi.descripcion,
                NULL as sucursal_destino,
                NULL as sucursal_origen,
                COUNT(DISTINCT mi.id_pieza) as total_tipos_piezas,
                SUM(mi.cantidad) as total_cantidad
            FROM movimientos_inventario mi
            WHERE mi.id_sucursal = %s 
            AND mi.tipo_movimiento IN ('alta_equipo_nuevo', 'alta_equipo_general', 'alta_admin_nuevo')
            AND mi.folio_nota_entrada IS NOT NULL
            GROUP BY mi.folio_nota_entrada, mi.fecha, mi.observaciones, mi.descripcion
            
            ORDER BY 
                CASE 
                    WHEN folio REGEXP '^[0-9]+$' THEN CAST(folio AS UNSIGNED)
                    ELSE 0
                END DESC,
                folio DESC
        """, (sucursal_id, sucursal_id, sucursal_id))
        
        transferencias = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'transferencias': transferencias
        })
        
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({'success': False, 'error': str(e)})


@bp_inventario.route('/historial-transferencias-page/<int:sucursal_id>')
@requiere_permiso('ver_inventario_sucursal')
def historial_transferencias_page(sucursal_id):
    """
    Página HTML dedicada para mostrar el historial de transferencias de una sucursal
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener información de la sucursal
        cursor.execute("SELECT id as id_sucursal, nombre FROM sucursales WHERE id = %s", (sucursal_id,))
        sucursal = cursor.fetchone()
        
        if not sucursal:
            flash('Sucursal no encontrada', 'error')
            return redirect(url_for('inventario.inventario_general'))
        
        # Obtener transferencias ENVIADAS, RECIBIDAS y ALTAS DE EQUIPO
        cursor.execute("""
            SELECT 
                'Enviado' as tipo,
                mi.folio_nota_salida as folio,
                DATE_FORMAT(mi.fecha, '%d/%m/%Y %H:%i') as fecha,
                mi.observaciones,
                mi.descripcion,
                sd.nombre as sucursal_destino,
                NULL as sucursal_origen
            FROM movimientos_inventario mi
            LEFT JOIN sucursales sd ON mi.sucursal_destino = sd.id
            WHERE mi.id_sucursal = %s 
            AND mi.tipo_movimiento = 'transferencia_salida'
            AND mi.folio_nota_salida IS NOT NULL
            GROUP BY mi.folio_nota_salida, mi.fecha, mi.observaciones, mi.descripcion, sd.nombre
            
            UNION ALL
            
            SELECT 
                'Recibido' as tipo,
                mi.folio_nota_entrada as folio,
                DATE_FORMAT(mi.fecha, '%d/%m/%Y %H:%i') as fecha,
                mi.observaciones,
                mi.descripcion,
                NULL as sucursal_destino,
                so.nombre as sucursal_origen
            FROM movimientos_inventario mi
            LEFT JOIN sucursales so ON mi.sucursal_destino = so.id
            WHERE mi.id_sucursal = %s 
            AND mi.tipo_movimiento = 'transferencia_entrada'
            AND mi.folio_nota_entrada IS NOT NULL
            GROUP BY mi.folio_nota_entrada, mi.fecha, mi.observaciones, mi.descripcion, so.nombre
            
            UNION ALL
            
            SELECT 
                'Alta Equipo' as tipo,
                mi.folio_nota_entrada as folio,
                DATE_FORMAT(mi.fecha, '%d/%m/%Y %H:%i') as fecha,
                mi.observaciones,
                mi.descripcion,
                NULL as sucursal_destino,
                NULL as sucursal_origen
            FROM movimientos_inventario mi
            WHERE mi.id_sucursal = %s 
            AND mi.tipo_movimiento IN ('alta_equipo_nuevo', 'alta_equipo_general', 'alta_admin_nuevo')
            AND mi.folio_nota_entrada IS NOT NULL
            GROUP BY mi.folio_nota_entrada, mi.fecha, mi.observaciones, mi.descripcion
            
            ORDER BY 
                CASE 
                    WHEN folio REGEXP '^[0-9]+$' THEN CAST(folio AS UNSIGNED)
                    ELSE 0
                END DESC,
                folio DESC
        """, (sucursal_id, sucursal_id, sucursal_id))
        
        transferencias = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('inventario/historial_transferencias.html', 
                             sucursal=sucursal, 
                             transferencias=transferencias)
        
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        flash('Error al cargar el historial de transferencias', 'error')
        return redirect(url_for('inventario.inventario_sucursal', sucursal_id=sucursal_id))
















