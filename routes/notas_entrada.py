from flask import Blueprint, jsonify, request, current_app, send_file, redirect, url_for
from datetime import datetime, timedelta
from utils.db import get_db_connection

from flask import send_file
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from PyPDF2 import PdfReader, PdfWriter

from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont



notas_entrada_bp = Blueprint('notas_entrada', __name__, url_prefix='/notas_entrada')


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
    return resultado['siguiente_folio'] if resultado and resultado['siguiente_folio'] else 1


@notas_entrada_bp.route('/preview/<int:renta_id>')
def preview_nota_entrada(renta_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener sucursal de la renta primero
    cursor.execute("SELECT id_sucursal FROM rentas WHERE id = %s", (renta_id,))
    sucursal_row = cursor.fetchone()
    if not sucursal_row:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Renta no encontrada'}), 404

    sucursal_id = sucursal_row['id_sucursal']

    # Folio consecutivo por sucursal (en lugar del global)
    folio_siguiente = obtener_siguiente_folio_nota_sucursal(cursor, sucursal_id)
    folio_entrada = str(folio_siguiente).zfill(5)

    # Datos de la renta y cliente
    cursor.execute("""
        SELECT r.id, r.fecha_entrada, r.direccion_obra, r.traslado, r.costo_traslado,
            c.nombre, c.apellido1, c.apellido2, c.telefono
        FROM rentas r
        JOIN clientes c ON r.cliente_id = c.id
        WHERE r.id = %s
    """, (renta_id,))
    renta = cursor.fetchone()
    if not renta:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Renta no encontrada'}), 404

    # Obtener folio de salida y nota_salida_id
    cursor.execute("""
        SELECT folio, id AS nota_salida_id
        FROM notas_salida
        WHERE renta_id = %s
        ORDER BY id DESC LIMIT 1
    """, (renta_id,))
    ns_row = cursor.fetchone()
    folio_salida = str(ns_row['folio']).zfill(5) if ns_row and ns_row['folio'] is not None else '-----'
    nota_salida_id = ns_row['nota_salida_id'] if ns_row else None

    # Fecha y hora actual
    fecha_hora = datetime.now().strftime('%d/%m/%Y %H:%M')

    # Fecha límite (un día después de fecha_entrada)
    fecha_limite = '--/--/---- --:--'
    estado = '---'
    dias_retraso = 0
    if renta['fecha_entrada']:
        fecha_base = renta['fecha_entrada']
        if isinstance(fecha_base, datetime):
            fecha_base = fecha_base.date()
        fecha_limite_dt = datetime.combine(fecha_base + timedelta(days=1), datetime.strptime('10:00', '%H:%M').time())
        fecha_limite = f"{fecha_limite_dt.strftime('%d/%m/%Y')} hasta las 10:00 a.m."
        ahora = datetime.now()
        if ahora <= fecha_limite_dt:
            estado = 'A tiempo'
        else:
            estado = 'Retrasada'
            delta = ahora - fecha_limite_dt
            dias_retraso = delta.days + (1 if delta.seconds > 0 else 0)

    # Piezas que salieron (de la nota de salida)
    piezas_salida = []
    if nota_salida_id:
        cursor.execute("""
            SELECT nsd.id_pieza, p.nombre_pieza, nsd.cantidad AS cantidad_esperada
            FROM notas_salida_detalle nsd
            JOIN piezas p ON nsd.id_pieza = p.id_pieza
            WHERE nsd.nota_salida_id = %s
        """, (nota_salida_id,))
        piezas_salida = cursor.fetchall()

    # Verifica si ya existe alguna nota de entrada
    cursor.execute("SELECT COUNT(*) AS total FROM notas_entrada WHERE renta_id = %s", (renta_id,))
    existe_entrada = cursor.fetchone()['total'] > 0

    # Consulta de piezas pendientes (si ya hay notas de entrada)
    cursor.execute("""
        SELECT
            nsd.id_pieza,
            p.nombre_pieza,
            nsd.cantidad AS cantidad_salida,
            IFNULL(SUM(ned.cantidad_recibida), 0) AS cantidad_recibida_total,
            (nsd.cantidad - IFNULL(SUM(ned.cantidad_recibida), 0)) AS cantidad_pendiente
        FROM notas_salida_detalle nsd
        JOIN piezas p ON nsd.id_pieza = p.id_pieza
        LEFT JOIN notas_entrada ne ON ne.renta_id = %s
        LEFT JOIN notas_entrada_detalle ned ON ned.nota_entrada_id = ne.id AND ned.id_pieza = nsd.id_pieza
        WHERE nsd.nota_salida_id = %s
        GROUP BY nsd.id_pieza, p.nombre_pieza, nsd.cantidad
        HAVING cantidad_pendiente > 0
    """, (renta_id, nota_salida_id))
    piezas_pendientes = cursor.fetchall()

    # Si hay piezas pendientes, muestra solo esas
    if piezas_pendientes:
        piezas = [
            {
                'id_pieza': p['id_pieza'],
                'nombre_pieza': p['nombre_pieza'],
                'cantidad_esperada': p['cantidad_pendiente']
            }
            for p in piezas_pendientes
        ]
    elif not existe_entrada:
        piezas = piezas_salida
    else:
        piezas = []

    cursor.close()
    conn.close()

    return jsonify({
        'folio_entrada': folio_entrada,
        'folio_salida': folio_salida,
        'nota_salida_id': nota_salida_id,
        'cliente': f"{renta['nombre']} {renta['apellido1']} {renta['apellido2']}",
        'telefono': renta['telefono'],
        'direccion_obra': renta['direccion_obra'],
        'traslado_original': renta['traslado'],
        'fecha_hora': fecha_hora,
        'fecha_limite': fecha_limite,
        'estado': estado,
        'dias_retraso': dias_retraso,
        'piezas': piezas
    })




####################################################################
####################################################################
####################################################################
####################################################################

@notas_entrada_bp.route('/crear/<int:renta_id>', methods=['POST'])
def crear_nota_entrada(renta_id):
    data = request.get_json()
    folio = data.get('folio_entrada')
    nota_salida_id = data.get('nota_salida_id')
    requiere_traslado_extra = data.get('traslado_extra', 'ninguno')
    costo_traslado_extra = float(data.get('costo_traslado_extra', 0))
    observaciones = data.get('observaciones', '')
    piezas = data.get('piezas', [])
    accion_devolucion = data.get('accion_devolucion', 'no')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cobrar_retraso = data.get('cobrar_retraso', False)
        estado_retraso = 'Retraso Pendiente' if cobrar_retraso else 'Sin Retraso'

        # Buscar si ya existe una nota de entrada en recolección para esta renta
        cursor.execute("""
            SELECT ne.id FROM notas_entrada ne
            WHERE ne.renta_id = %s
            AND (
                SELECT COUNT(*) FROM notas_entrada_detalle ned
                WHERE ned.nota_entrada_id = ne.id
                AND (ned.cantidad_recibida IS NULL OR ned.cantidad_recibida = 0)
            ) = (SELECT COUNT(*) FROM notas_entrada_detalle WHERE nota_entrada_id = ne.id)
            LIMIT 1
        """, (renta_id,))
        nota_existente = cursor.fetchone()

        if nota_existente:
            nota_entrada_id = nota_existente['id']
            # Actualizar cabecera
            cursor.execute("""
                UPDATE notas_entrada
                SET requiere_traslado_extra=%s, costo_traslado_extra=%s, observaciones=%s, estado_retraso=%s, accion_devolucion=%s, fecha_entrada_real=NOW()
                WHERE id=%s
            """, (requiere_traslado_extra, costo_traslado_extra, observaciones, estado_retraso, accion_devolucion, nota_entrada_id))
            # Eliminar detalles anteriores
            cursor.execute("DELETE FROM notas_entrada_detalle WHERE nota_entrada_id=%s", (nota_entrada_id,))
        else:
            # Insertar nota de entrada 
            cursor.execute("""
                INSERT INTO notas_entrada (
                    folio, renta_id, nota_salida_id, fecha_entrada_real,
                    requiere_traslado_extra, costo_traslado_extra, observaciones, estado, created_at, estado_retraso, accion_devolucion
                ) VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, NOW(), %s, %s)
            """, (
                folio, renta_id, nota_salida_id, requiere_traslado_extra,
                costo_traslado_extra, observaciones, 'normal', estado_retraso, accion_devolucion
            ))
            nota_entrada_id = cursor.lastrowid

        # Obtener sucursal de la renta
        cursor.execute("SELECT id_sucursal FROM rentas WHERE id = %s", (renta_id,))
        row = cursor.fetchone()
        id_sucursal = row['id_sucursal'] if row else None

        # Insertar detalle y actualizar inventario
        for pieza in piezas:
            id_pieza = pieza['id_pieza']
            cantidad_esperada = pieza['cantidad_esperada']

            def safe_int(val):
                return int(val) if str(val).isdigit() else 0

            cantidad_recibida = safe_int(pieza.get('cantidad_recibida', 0))
            cantidad_buena = safe_int(pieza.get('cantidad_buena', 0))
            cantidad_danada = safe_int(pieza.get('cantidad_danada', 0))
            cantidad_sucia = safe_int(pieza.get('cantidad_sucia', 0))
            cantidad_perdida = safe_int(pieza.get('cantidad_perdida', 0))
            observaciones_pieza = pieza.get('observaciones_pieza', '')

            cursor.execute("""
                INSERT INTO notas_entrada_detalle (
                    nota_entrada_id, id_pieza, cantidad_esperada, cantidad_recibida,
                    cantidad_buena, cantidad_danada, cantidad_sucia, cantidad_perdida, observaciones_pieza
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                nota_entrada_id, id_pieza, cantidad_esperada, cantidad_recibida,
                cantidad_buena, cantidad_danada, cantidad_sucia, cantidad_perdida, observaciones_pieza
            ))

            # Actualizar inventario solo si hay cantidades recibidas
            cursor.execute("""
                SELECT id_inventario FROM inventario_sucursal
                WHERE id_sucursal = %s AND id_pieza = %s
            """, (id_sucursal, id_pieza))
            inventario_row = cursor.fetchone()
            if not inventario_row:
                continue

            # Buenas: +disponibles, -rentadas
            cursor.execute("""
                UPDATE inventario_sucursal
                SET 
                    disponibles = disponibles + %s,
                    rentadas = rentadas - %s
                WHERE id_sucursal = %s AND id_pieza = %s
            """, (
                cantidad_buena, cantidad_buena, id_sucursal, id_pieza
            ))

            # Dañadas: +daniadas, -rentadas
            if cantidad_danada > 0:
                cursor.execute("""
                    UPDATE inventario_sucursal
                    SET 
                        daniadas = daniadas + %s,
                        rentadas = rentadas - %s
                    WHERE id_sucursal = %s AND id_pieza = %s
                """, (
                    cantidad_danada, cantidad_danada, id_sucursal, id_pieza
                ))

            # Perdidas: solo si recibidas == esperadas
            if cantidad_recibida == cantidad_esperada and cantidad_perdida > 0:
                cursor.execute("""
                    UPDATE inventario_sucursal
                    SET 
                        perdidas = perdidas + %s,
                        rentadas = rentadas - %s,
                        total = total - %s
                    WHERE id_sucursal = %s AND id_pieza = %s
                """, (
                    cantidad_perdida, cantidad_perdida, cantidad_perdida, id_sucursal, id_pieza
                ))

        # --- NUEVO FLUJO DE ESTADO ---
        # Detectar si la nota es de recolección (todas las recibidas en 0)
        es_recoleccion = all(
            (pieza.get('cantidad_recibida', 0) in [0, '', None]) for pieza in piezas
        )

        if es_recoleccion:
            cursor.execute("""
                UPDATE rentas SET estado_renta = 'en recolección'
                WHERE id = %s
            """, (renta_id,))
        else:
            # Verificar si quedan piezas pendientes después de esta nota
            cursor.execute("""
                SELECT
                    SUM(nsd.cantidad) AS total_salieron,
                    IFNULL(SUM(ned.cantidad_recibida), 0) AS total_recibidas
                FROM notas_salida_detalle nsd
                LEFT JOIN notas_entrada ne ON ne.renta_id = %s
                LEFT JOIN notas_entrada_detalle ned ON ned.nota_entrada_id = ne.id AND ned.id_pieza = nsd.id_pieza
                WHERE nsd.nota_salida_id = %s
            """, (renta_id, nota_salida_id))
            row = cursor.fetchone()
            total_salieron = row['total_salieron'] or 0
            total_recibidas = row['total_recibidas'] or 0

            if total_salieron == total_recibidas:
                cursor.execute("""
                    UPDATE rentas SET estado_renta = 'finalizada'
                    WHERE id = %s
                """, (renta_id,))
            else:
                cursor.execute("""
                    UPDATE rentas SET estado_renta = 'activo'
                    WHERE id = %s
                """, (renta_id,))

        # Activar estado de extra pendiente si hay cobros extra
        def safe_int(val):
            try:
                return int(val)
            except (ValueError, TypeError):
                return 0

        hay_cobro_extra = any(
            safe_int(pieza.get('cantidad_danada', 0)) > 0 or
            safe_int(pieza.get('cantidad_sucia', 0)) > 0 or
            safe_int(pieza.get('cantidad_perdida', 0)) > 0
            for pieza in piezas
        )

        if requiere_traslado_extra in ['medio', 'redondo'] and costo_traslado_extra > 0:
            hay_cobro_extra = True

        if hay_cobro_extra:
            cursor.execute("""
                UPDATE rentas SET estado_cobro_extra = 'Extra Pendiente'
                WHERE id = %s
            """, (renta_id,))
        else:
            cursor.execute("""
                UPDATE rentas SET estado_cobro_extra = NULL
                WHERE id = %s
            """, (renta_id,))

        conn.commit()
        return jsonify({'success': True, 'nota_entrada_id': nota_entrada_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()




####################################################################
####################################################################
####################################################################
####################################################################


@notas_entrada_bp.route('/historial/<int:renta_id>')
def historial_notas_entrada(renta_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, folio, fecha_entrada_real
        FROM notas_entrada
        WHERE renta_id = %s
        ORDER BY fecha_entrada_real DESC
    """, (renta_id,))
    notas = cursor.fetchall()
    cursor.close()
    conn.close()
    # Convert datetime to string for JSON
    for nota in notas:
        if isinstance(nota['fecha_entrada_real'], datetime):
            nota['fecha_entrada_real'] = nota['fecha_entrada_real'].strftime('%Y-%m-%d %H:%M')
    return jsonify(notas)



####################################################################
####################################################################
####################################################################
####################################################################



@notas_entrada_bp.route('/pdf/<int:nota_entrada_id>')
def generar_pdf_nota_entrada(nota_entrada_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT ne.folio, ne.fecha_entrada_real, ne.requiere_traslado_extra, ne.costo_traslado_extra, ne.observaciones,
               r.direccion_obra,
               CONCAT(c.nombre, ' ', c.apellido1, ' ', c.apellido2) AS cliente_nombre, c.codigo_cliente,
               c.telefono
        FROM notas_entrada ne
        JOIN rentas r ON ne.renta_id = r.id
        JOIN clientes c ON r.cliente_id = c.id
        WHERE ne.id = %s
    """, (nota_entrada_id,))
    nota = cursor.fetchone()

    cursor.execute("""
        SELECT ned.cantidad_esperada, ned.cantidad_recibida, ned.cantidad_buena, ned.cantidad_danada, ned.cantidad_sucia, ned.cantidad_perdida, p.nombre_pieza
        FROM notas_entrada_detalle ned
        JOIN piezas p ON ned.id_pieza = p.id_pieza
        WHERE ned.nota_entrada_id = %s
    """, (nota_entrada_id,))
    piezas = cursor.fetchall()

    cursor.close()
    conn.close()

    # --- Generar PDF con plantilla ---
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    pdfmetrics.registerFont(TTFont('Carlito', os.path.join(current_app.root_path, 'static/fonts/Carlito-Regular.ttf')))

    #Folio de Nota de Entrada
    can.setFont("Carlito", 9)
    texto = "FOLIO DE ENTRADA:"
    x = 450
    y = 670
    can.drawString(x, y, texto)

    # Dibuja el folio en tamaño 16, justo después del texto
    folio_str = f"#{str(nota['folio']).zfill(5)}"
    can.setFont("Helvetica-Bold", 12)
    x_folio = x + can.stringWidth(texto, "Helvetica-Bold", 10) - 25
    can.drawString(x_folio, y, folio_str)
    

    ## NOMBRE DEL CLIENTE
    can.setFont("Carlito", 10)
    cliente_completo = f"{nota['codigo_cliente']} - {nota['cliente_nombre'].upper()}"
    can.drawString(63, 703, f"{cliente_completo}")


    can.setFont("Helvetica", 10)
    can.drawString(479, 708, f" {nota['fecha_entrada_real'].strftime('%d/%m/%Y %H:%M')}")
    
    can.drawString(67, 671, f" {nota['telefono']}")

    can.setFont("Helvetica-Bold", 10)
    can.drawString(67, 657, f" {nota['cliente_nombre']}")
    
   


    y = 630
    can.setFont("Helvetica-Bold", 10)
   

    y -= 15
    can.setFont("Helvetica-Bold", 9)
    can.drawString(60, y, "Pieza")
    can.drawString(250, y, "Esperadas")
    can.drawString(300, y, "Recibidas")
    can.drawString(375, y, "Buenas")
    can.drawString(420, y, "Dañadas")
    can.drawString(470, y, "Sucias")
    can.drawString(510, y, "Perdidas")

    y -= 13
    can.setFont("Helvetica", 9)
    for pieza in piezas:
        def mostrar_vacio_si_cero(val):
            return "" if val == 0 else str(val)
        can.drawString(60, y, f"{pieza['nombre_pieza']}")
        can.drawString(250, y, str(pieza['cantidad_esperada']))
        can.drawString(300, y, mostrar_vacio_si_cero(pieza['cantidad_recibida']))
        can.drawString(375, y, mostrar_vacio_si_cero(pieza['cantidad_buena']))
        can.drawString(420, y, mostrar_vacio_si_cero(pieza['cantidad_danada']))
        can.drawString(470, y, mostrar_vacio_si_cero(pieza['cantidad_sucia']))
        can.drawString(510, y, mostrar_vacio_si_cero(pieza['cantidad_perdida']))
        y -= 13

        if y < 100:
            can.showPage()
            y = 750

    y -= 10
    can.setFont("Helvetica", 10)
    can.drawString(60, y, f"DIRECCIÓN DE OBRA: {nota['direccion_obra'] or 'Sin dirección'}")
    y -= 13
           

    # === FIRMAS ===
    y -= 30
    can.setFont("Carlito", 10)
    # Línea para firma de la empresa (Andamios Colosio)
    can.line(60, y, 250, y)
    # Línea para firma del cliente
    can.line(350, y, 540, y)

    y -= 15
    # Etiquetas de firmas
    can.drawString(60, y, "RECIBE: ANDAMIOS COLOSIO")
    can.drawString(350, y, f"ENTREGA:")


    
    y -= 10
    can.setFont("Helvetica-Bold", 10)
    can.drawString(60, y, "Observaciones:")
    y -= 13
    can.setFont("Helvetica", 10)
    can.drawString(60, y, nota['observaciones'] or "Ninguna")

    can.save()
    packet.seek(0)

    # --- Combinar con plantilla ---
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
        overlay_pdf = PdfReader(packet)
        output = PdfWriter()
        output.add_page(overlay_pdf.pages[0])

    output_stream = BytesIO()
    output.write(output_stream)
    output_stream.seek(0)

    return send_file(
        output_stream,
        download_name=f"nota_entrada_{str(nota['folio']).zfill(5)}.pdf",
        mimetype='application/pdf'
    )




@notas_entrada_bp.route('/pdf_renta/<int:renta_id>')
def generar_pdf_nota_entrada_por_renta(renta_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id FROM notas_entrada
        WHERE renta_id = %s
        ORDER BY id DESC
        LIMIT 1
    """, (renta_id,))
    nota = cursor.fetchone()
    cursor.close()
    conn.close()
    if not nota:
        return f"No hay nota de entrada para la renta {renta_id}", 404
    return redirect(url_for('notas_entrada.generar_pdf_nota_entrada', nota_entrada_id=nota['id']))