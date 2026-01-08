
import os
from io import BytesIO
from datetime import datetime
from flask import Blueprint, redirect, request, jsonify, send_file, current_app, url_for
from utils.db import get_db_connection

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PyPDF2 import PdfReader, PdfWriter
from num2words import num2words 
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


prefactura_bp = Blueprint('prefactura', __name__, url_prefix='/prefactura')

# === Endpoint: Obtener datos de prefactura (AJAX) ===
@prefactura_bp.route('/<int:renta_id>')
def obtener_prefactura(renta_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Detalle de productos
    cursor.execute("""
        SELECT p.nombre, d.cantidad, d.dias_renta, d.costo_unitario, d.subtotal
        FROM renta_detalle d
        JOIN productos p ON d.id_producto = p.id_producto
        WHERE d.renta_id = %s
    """, (renta_id,))
    detalle = cursor.fetchall()
    # Totales y traslado
    cursor.execute("""
        SELECT total_con_iva, traslado, costo_traslado, fecha_entrada

        FROM rentas
        WHERE id = %s
    """, (renta_id,))
    total_info = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({
        "detalle": detalle,
        "total_con_iva": total_info['total_con_iva'] if total_info else 0,
        "traslado": total_info['traslado'] if total_info else None,
        "costo_traslado": total_info['costo_traslado'] if total_info else 0
    })




@prefactura_bp.route('/api/pagos/<int:renta_id>')
def obtener_historial_pagos(renta_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT id, tipo, metodo_pago, monto, DATE_FORMAT(fecha_emision, '%d/%m/%Y %H:%i') as fecha_emision
        FROM prefacturas
        WHERE renta_id = %s AND pagada = 1
        ORDER BY fecha_emision ASC
    ''', (renta_id,))
    pagos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(pagos)

@prefactura_bp.route('/api/info-redondeo/<int:renta_id>')
def obtener_info_redondeo(renta_id):
    """Obtiene información sobre si se debe aplicar redondeo basado en el primer abono"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verificar si ya hay abonos y cuál fue el primer método
    cursor.execute("""
        SELECT COUNT(*) as total_abonos,
               COALESCE(SUM(monto), 0) as total_pagado,
               (SELECT metodo_pago FROM prefacturas WHERE renta_id = %s AND tipo = 'abono' AND pagada = 1 ORDER BY fecha_emision ASC LIMIT 1) as primer_metodo
        FROM prefacturas 
        WHERE renta_id = %s AND tipo = 'abono' AND pagada = 1
    """, (renta_id, renta_id))
    abono_info = cursor.fetchone()
    
    # Obtener total de la renta
    cursor.execute("SELECT total_con_iva FROM rentas WHERE id = %s", (renta_id,))
    renta_info = cursor.fetchone()
    total_renta = renta_info['total_con_iva'] if renta_info else 0
    
    cursor.close()
    conn.close()
    
    es_primer_abono = abono_info['total_abonos'] == 0
    total_ya_pagado = float(abono_info['total_pagado']) if abono_info['total_pagado'] is not None else 0.0
    primer_metodo_abono = abono_info['primer_metodo']
    saldo_pendiente = float(total_renta) - total_ya_pagado
    
    # Determinar si se debe aplicar redondeo
    aplicar_redondeo = False
    if es_primer_abono:
        aplicar_redondeo = True  
    else:
        aplicar_redondeo = primer_metodo_abono == 'EFECTIVO'
    
    return jsonify({
        'es_primer_abono': es_primer_abono,
        'primer_metodo_abono': primer_metodo_abono,
        'saldo_pendiente': saldo_pendiente,
        'total_renta': total_renta,
        'total_pagado': total_ya_pagado,
        'aplicar_redondeo': aplicar_redondeo
    })




# === Endpoint: Registrar pago 
@prefactura_bp.route('/pago/<int:renta_id>', methods=['POST'])
def registrar_pago_prefactura(renta_id):
    data = request.get_json()
    tipo = data.get('tipo', 'inicial')
    metodo = data.get('metodo_pago')
    monto = data.get('monto')
    monto_recibido = data.get('monto_recibido')
    cambio = data.get('cambio')
    facturable = data.get('facturable', False)
    numero_seguimiento = data.get('numero_seguimiento')

    # DEBUG: Imprimir todos los datos recibidos
    print(f"=== DEBUG PREFACTURA ===")
    print(f"metodo_pago: '{metodo}' (tipo: {type(metodo)})")
    print(f"monto: {monto}")
    print(f"monto_recibido: {monto_recibido}")
    print(f"cambio: {cambio}")
    print(f"numero_seguimiento: '{numero_seguimiento}'")
    print(f"facturable: {facturable}")
    
    # Validar método de pago
    if not metodo or metodo.strip() == '':
        print("ERROR: Método de pago vacío o None")
        return jsonify({'success': False, 'error': 'Método de pago requerido'}), 400
    
    # Convertir explícitamente a entero para la BD
    facturable_int = 1 if facturable else 0
    
    # Asegurar que cambio no sea None para métodos no efectivo
    if metodo.upper() != 'EFECTIVO':
        cambio = 0.0
        # Asegurar que numero_seguimiento no sea None
        if not numero_seguimiento:
            numero_seguimiento = ''

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Función para redondear según reglas de efectivo
        def redondear_efectivo(monto):
            entero = int(monto)
            centavos = round((monto - entero) * 100)
            if centavos <= 49:
                return entero
            elif centavos >= 60:
                return entero + 1
            else:
                return entero + 0.5

        # Aplicar redondeo para pagos iniciales en efectivo
        if tipo == 'inicial' and metodo.upper() == 'EFECTIVO':
            monto_original = float(monto)
            monto_redondeado = redondear_efectivo(monto_original)
            print(f"Pago inicial efectivo - Monto original: {monto_original}, Monto redondeado: {monto_redondeado}")
            monto = monto_redondeado
            # Recalcular cambio si es necesario
            if monto_recibido and float(monto_recibido) > monto_redondeado:
                cambio = float(monto_recibido) - monto_redondeado

        # Verificar si es el primer abono para aplicar redondeo
        if tipo == 'abono':
            cursor.execute("""
                SELECT COUNT(*) as total_abonos, 
                       COALESCE(SUM(monto), 0) as total_pagado,
                       (SELECT metodo_pago FROM prefacturas WHERE renta_id = %s AND tipo = 'abono' AND pagada = 1 ORDER BY fecha_emision ASC LIMIT 1) as primer_metodo
                FROM prefacturas 
                WHERE renta_id = %s AND tipo = 'abono' AND pagada = 1
            """, (renta_id, renta_id))
            abono_info = cursor.fetchone()
            es_primer_abono = abono_info[0] == 0
            total_ya_pagado = abono_info[1]
            primer_metodo_abono = abono_info[2]
            
            # Obtener total de la renta
            cursor.execute("SELECT total_con_iva FROM rentas WHERE id = %s", (renta_id,))
            total_renta = cursor.fetchone()[0]
            saldo_pendiente = total_renta - total_ya_pagado
            
            print(f"es_primer_abono: {es_primer_abono}, primer_metodo: {primer_metodo_abono}, saldo_pendiente: {saldo_pendiente}")
            

            # Aplicar redondeo solo si es el primer abono Y es efectivo
            if es_primer_abono and metodo.upper() == 'EFECTIVO':
                saldo_redondeado = redondear_efectivo(saldo_pendiente)
                print(f"Saldo original: {saldo_pendiente}, Saldo redondeado: {saldo_redondeado}")
                # Si el monto a pagar es mayor o igual al saldo pendiente original, es liquidación
                if float(monto) >= saldo_pendiente:
                    monto = saldo_redondeado  # Cobrar el monto redondeado
                    if float(monto_recibido) > saldo_redondeado:
                        cambio = float(monto_recibido) - saldo_redondeado
                    # Forzar saldo pendiente a cero si se liquida con redondeo
                    saldo_pendiente = 0.0

        # --- Nueva lógica: Si el primer abono fue efectivo y se redondeó, nunca mostrar los centavos en abonos futuros ---
        # Esto se aplica a todos los métodos de pago en abonos posteriores
        cursor.execute("""
            SELECT COUNT(*) as total_abonos,
                   (SELECT metodo_pago FROM prefacturas WHERE renta_id = %s AND tipo = 'abono' AND pagada = 1 ORDER BY fecha_emision ASC LIMIT 1) as primer_metodo
            FROM prefacturas 
            WHERE renta_id = %s AND tipo = 'abono' AND pagada = 1
        """, (renta_id, renta_id))
        abono_info2 = cursor.fetchone()
        primer_metodo_abono2 = abono_info2[1]
        if primer_metodo_abono2 == 'EFECTIVO':
            # Buscar el primer abono efectivo y ver si hubo redondeo
            cursor.execute("""
                SELECT monto, (SELECT total_con_iva FROM rentas WHERE id = %s) as total_renta
                FROM prefacturas WHERE renta_id = %s AND tipo = 'abono' AND pagada = 1 ORDER BY fecha_emision ASC LIMIT 1
            """, (renta_id, renta_id))
            primer_abono = cursor.fetchone()
            if primer_abono:
                monto_abono = float(primer_abono[0])
                total_renta = float(primer_abono[1])
                # Si el monto del primer abono no tiene centavos, asumimos que hubo redondeo
                if abs(monto_abono - round(monto_abono)) in [0, 0.5, 1]:
                    # Forzar saldo pendiente a 0 si ya se liquidó el monto redondeado
                    cursor.execute("""
                        SELECT COALESCE(SUM(monto),0) as total_pagado
                        FROM prefacturas
                        WHERE renta_id = %s AND pagada = 1
                    """, (renta_id,))
                    total_pagado = float(cursor.fetchone()[0])
                    if total_pagado >= monto_abono:
                        saldo_pendiente = 0.0
                
        # Insertar la prefactura (abono o inicial)
        cursor.execute("""
            INSERT INTO prefacturas (
            renta_id, fecha_emision, tipo, pagada, metodo_pago, monto, 
            monto_recibido, cambio, numero_seguimiento, generada, facturable
        ) VALUES (%s, NOW() - INTERVAL 6 HOUR, %s, 1, %s, %s, %s, %s, %s, 1, %s)
        """, (
            renta_id, tipo, metodo.upper(), monto, monto_recibido, cambio, 
            numero_seguimiento, facturable_int  
        ))
        prefactura_id = cursor.lastrowid

        # Calcular el total pagado hasta ahora (sumar todas las prefacturas pagadas de la renta)
        cursor.execute("""
            SELECT COALESCE(SUM(monto),0) as total_pagado
            FROM prefacturas
            WHERE renta_id = %s AND pagada = 1
        """, (renta_id,))
        total_pagado = cursor.fetchone()[0]

        # Obtener el total a pagar de la renta
        cursor.execute("SELECT total_con_iva FROM rentas WHERE id = %s", (renta_id,))
        total_renta = cursor.fetchone()[0]

        # Determinar el nuevo estado de pago
        if total_pagado >= total_renta:
            nuevo_estado = 'Pago realizado'
        elif total_pagado > 0:
            nuevo_estado = 'Saldo pendiente'
        else:
            nuevo_estado = 'Pago pendiente'

        # Actualizar el estado de la renta
        cursor.execute("""
            UPDATE rentas SET estado_pago=%s, metodo_pago=%s WHERE id=%s
        """, (nuevo_estado, metodo.upper(), renta_id))

        conn.commit()

        # VERIFICAR QUE SE GUARDÓ CORRECTAMENTE
        cursor.execute("SELECT metodo_pago, numero_seguimiento FROM prefacturas WHERE id = %s", (prefactura_id,))
        verificacion = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'prefactura_id': prefactura_id})
    except Exception as e:
        print(f"Error al registrar prefactura: {e}")
        return jsonify({'success': False, 'error': str(e)})















@prefactura_bp.route('/pdf/<int:prefactura_id>')
def generar_pdf_prefactura(prefactura_id):
    # --- OBTENER DATOS COMPLETOS DEL CLIENTE ---
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, r.fecha_entrada, r.fecha_salida, r.direccion_obra, r.metodo_pago, r.iva,
               r.traslado, r.costo_traslado,
               CONCAT(c.nombre, ' ', c.apellido1, ' ', c.apellido2) AS cliente_nombre,
               c.codigo_cliente,
               c.telefono,
               c.correo,
               c.calle,
               c.numero_exterior,
               c.numero_interior,
               c.entre_calles,
               c.colonia,
               c.codigo_postal,    
               c.municipio,
               c.estado,
               c.rfc
        FROM prefacturas p
        JOIN rentas r ON p.renta_id = r.id
        JOIN clientes c ON r.cliente_id = c.id
        WHERE p.id = %s
    """, (prefactura_id,))
    prefactura = cursor.fetchone()

    cursor.execute("""
        SELECT prod.nombre, rd.cantidad, rd.dias_renta, rd.costo_unitario, rd.subtotal
        FROM renta_detalle rd
        JOIN productos prod ON rd.id_producto = prod.id_producto
        WHERE rd.renta_id = %s
    """, (prefactura['renta_id'],))
    detalles = cursor.fetchall()
    cursor.close()
    conn.close()

    # --- GENERAR OVERLAY CON DATOS ---
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    pdfmetrics.registerFont(TTFont('Carlito', os.path.join(current_app.root_path, 'static/fonts/Carlito-Regular.ttf')))

    # === INFORMACIÓN DEL CLIENTE ===
    can.setFont("Carlito", 10)
    
    # Código y nombre del cliente
    cliente_codigo_nombre = f"{prefactura['codigo_cliente']} - {prefactura['cliente_nombre'].upper()}"
    can.drawString(62, 703, f"{cliente_codigo_nombre}")
    
    # Teléfono
    can.drawString(70, 656, f"{prefactura['telefono'] or 'No registrado'}")
    
    # Correo
    can.drawString(62, 640.5
                   , f"{prefactura['correo'] or 'No registrado'}")
    
    # Dirección (calle, número y entre calles)
    direccion_completa = prefactura['calle'] or ''
    if prefactura['numero_exterior']:
        direccion_completa += f" {prefactura['numero_exterior']}"
    if prefactura['numero_interior']:
        direccion_completa += f", Int. {prefactura['numero_interior']}"
    if prefactura['entre_calles']:
        direccion_completa += f" (entre {prefactura['entre_calles']})"
    if prefactura['colonia']:
        direccion_completa += f", COL. {prefactura['colonia']}"
    if prefactura['codigo_postal']:
        direccion_completa += f" - C.P. {prefactura['codigo_postal']}"

    
    can.drawString(73, 687, f"{direccion_completa.upper()}")
    
    # Estado y Municipio
    can.drawString(60, 671, f"{prefactura['estado'] or 'No registrado'.upper()}")
    can.drawString(290, 671, f"{prefactura['municipio'] or 'No registrado'.upper()}")
    
    # RFC
    can.drawString(290, 639.5, f"{prefactura['rfc'] or 'No registrado'.upper()}")
    
    # Facturable
    facturable_texto = "SÍ" if prefactura['facturable'] else "NO"
    can.drawString(458, 638.5, f"{facturable_texto}")
    
        # === FECHA Y HORA DE EMISIÓN (HORA DE CAMPECHE) ===
    can.setFont("Carlito", 10)
    # La fecha ya viene en hora de Campeche desde la BD
    fecha_emision = prefactura['fecha_emision']
    can.drawString(482, 708, f"{fecha_emision.strftime('%d/%m/%Y')} - {fecha_emision.strftime('%H:%M:%S')}")
    
    # Folio
    can.setFont("Carlito", 10)
    can.drawString(564, 725, f"#{prefactura_id}")

    # === TABLA DE PRODUCTOS ===
    can.setFont("Carlito", 10)
    
    # Datos de productos
    y = 605
    subtotal_general = 0
    
    for item in detalles:
        can.drawString(50, y, item['nombre'][:40])  # Limitar longitud del nombre
        can.drawRightString(347, y, str(item['cantidad']))
        can.drawRightString(405, y, str(item['dias_renta'] or 'N/A'))
        can.drawRightString(495, y, f"${item['costo_unitario']:.2f}")
        can.drawRightString(570, y, f"${item['subtotal']:.2f}")
        
        subtotal_general += float(item['subtotal'])
        y -= 18
        
        # Si hay muchos productos, crear nueva página o ajustar
        if y < 300:
            break

        # === LÍNEA DIVISORA Y TOTALES ===
    y -= 15
    can.line(28, y+15, 585, y+15)  # Línea separadora

    espacio_3mm = 10
    can.setFont("Carlito", 11)
    y_totales = y + 10 - espacio_3mm  # 3mm debajo de la línea

    # PERÍODO DE RENTA (AL LADO IZQUIERDO DEL SUBTOTAL)
    periodo_renta = f"{prefactura['fecha_salida'].strftime('%d/%m/%Y')}"
    if prefactura['fecha_entrada']:
        periodo_renta += f" - {prefactura['fecha_entrada'].strftime('%d/%m/%Y')}"
    else:
        periodo_renta += " - Indefinido"
    can.setFont("Carlito", 10)
    can.drawString(60, y_totales, f"PERIODO DE RENTA: {periodo_renta}")

    # Subtotal de productos (AL LADO DERECHO)
    can.setFont("Carlito", 11)
    can.drawString(400, y_totales, "SUBTOTAL:")
    can.drawRightString(570, y_totales, f"${subtotal_general:.2f}")
    y_totales -= 15

    # Traslado
    traslado_tipo = prefactura.get('traslado', 'ninguno')
    costo_traslado = prefactura.get('costo_traslado', 0)
    can.drawString(400, y_totales, f"TRASLADO ({traslado_tipo}):")
    can.drawRightString(570, y_totales, f"${costo_traslado:.2f}")
    y_totales -= 15

    # IVA
    can.drawString(400, y_totales, "IVA (16%):")
    can.drawRightString(570, y_totales, f"${prefactura['iva']:.2f}")
    y_totales -= 20

    # Total final
    can.setFont("Helvetica-Bold", 11)
    can.drawString(400, y_totales, "TOTAL:")
    can.drawRightString(570, y_totales, f"${prefactura['monto']:.2f}")

    # === MÉTODO DE PAGO (DEBAJO DEL TOTAL) ===
    y_totales -= 15
    can.setFont("Carlito", 11)
    can.drawString(400, y_totales, "MÉTODO/PAGO:")
    can.drawRightString(570, y_totales, f"{prefactura['metodo_pago']}")

    # === TOTAL EN LETRAS (AL LADO IZQUIERDO) ===
    monto = prefactura['monto']
    monto_entero = int(monto)
    monto_centavos = int(round((monto - monto_entero) * 100))
    monto_letras = num2words(monto_entero, lang='es').upper()
    if monto_centavos > 0:
        monto_letras = f"{monto_letras} PESOS CON {monto_centavos:02d}/100 M.N."
    else:
        monto_letras = f"{monto_letras} PESOS 00/100 M.N."

    # Posicionar el total en letras al lado izquierdo del método de pago
    can.drawString(60, y_totales, f"SON: {monto_letras}")   
   

    # === AVISOS IMPORTANTES PARA EL CLIENTE ===
    y_avisos = y_totales - 10  # Más espacio entre totales y avisos

    # Línea separadora para los avisos
    can.line(28, y_avisos + 5, 585, y_avisos + 5)
    y_avisos -= 5

    # REQUISITOS DE CLIENTE
    can.setFont("Helvetica-Bold", 10)
    can.drawString(60, y_avisos, "REQUISITOS DE CLIENTE:")
    y_avisos -= 12

    can.setFont("Helvetica", 8)
    can.drawString(60, y_avisos, "LOS SIGUIENTES DOCUMENTOS PUEDEN SER EN IMAGEN O EN COPIA IMPRESA:")
    y_avisos -= 12

    can.drawString(70, y_avisos, "• IDENTIFICACIÓN OFICIAL.")
    y_avisos -= 10

    can.drawString(70, y_avisos, "• LICENCIA DE CONDUCIR.")
    y_avisos -= 10

    can.drawString(70, y_avisos, "• CONSTANCIA DE SITUACIÓN FISCAL.")
    y_avisos -= 10

    can.drawString(70, y_avisos, "• COMPROBANTE DE DOMICILIO.")
    y_avisos -= 15

    # REQUISITOS DE RENTA
    can.setFont("Helvetica-Bold", 10)
    can.drawString(60, y_avisos, "REQUISITOS DE RENTA:")
    y_avisos -= 11

    can.setFont("Helvetica", 8)
    can.drawString(70, y_avisos, "• SE REQUIERE EL PAGO COMPLETO POR ADELANTADO DE LA RENTA.")
    y_avisos -= 10

    can.drawString(70, y_avisos, "• UBICACIÓN EXACTA DE LA OBRA (POR GOOGLE MAPS)")
    y_avisos -= 15

    # ¡IMPORTANTE!
    can.setFont("Helvetica-Bold", 10)
    can.drawString(60, y_avisos, "¡IMPORTANTE!")
    y_avisos -= 11

    can.setFont("Helvetica", 8)
    can.drawString(70, y_avisos, "• EL PERIODO DE RENTA INCLUYE DOMINGOS, DÍAS INHÁBILES Y FESTIVOS.")
    y_avisos -= 10

    can.drawString(70, y_avisos, "• NO SE ARMA, NI SE DESARMA EL EQUIPO.")


    # Guardar el canvas
    can.save()
    packet.seek(0)

    # --- COMBINAR CON LA PLANTILLA (SI TIENES) ---
    try:
        plantilla_path = os.path.join(current_app.root_path, 'static/notas/prefactura_plantilla.pdf')
        if os.path.exists(plantilla_path):
            plantilla_pdf = PdfReader(plantilla_path)
            overlay_pdf = PdfReader(packet)
            output = PdfWriter()

            page = plantilla_pdf.pages[0]
            page.merge_page(overlay_pdf.pages[0])
            output.add_page(page)
        else:
            # Si no hay plantilla, usar solo el overlay
            overlay_pdf = PdfReader(packet)
            output = PdfWriter()
            output.add_page(overlay_pdf.pages[0])
    except Exception as e:
        print(f"Error con plantilla, usando solo overlay: {e}")
        overlay_pdf = PdfReader(packet)
        output = PdfWriter()
        output.add_page(overlay_pdf.pages[0])

    output_stream = BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    
    return send_file(
        output_stream, 
        download_name=f"prefactura_{prefactura_id}.pdf", 
        mimetype='application/pdf'
    )

@prefactura_bp.route('/pdf_renta/<int:renta_id>')
def generar_pdf_prefactura_por_renta(renta_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Buscar prefactura por renta_id
    cursor.execute("SELECT id FROM prefacturas WHERE renta_id = %s ORDER BY id DESC LIMIT 1", (renta_id,))
    prefactura = cursor.fetchone()
    if not prefactura:
        return f"No hay prefactura para la renta {renta_id}", 404
    # Redirigir a la función original con el id de prefactura encontrado
    return redirect(url_for('prefactura.generar_pdf_prefactura', prefactura_id=prefactura['id']))