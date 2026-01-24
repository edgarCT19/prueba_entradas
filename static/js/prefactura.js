document.addEventListener('DOMContentLoaded', function () {

    // Función para redondear según las reglas de efectivo
    function redondearEfectivo(monto) {
        if (!monto || isNaN(monto)) return 0;
        const entero = Math.floor(monto);
        const centavos = Math.round((monto - entero) * 100);
        if (centavos <= 49) return entero;
        if (centavos >= 60) return entero + 1;
        return entero + 0.5;
    }

    // Permite abrir el modal desde el flujo principal y seleccionar el tipo automáticamente
    window.abrirModalPrefacturaPago = function (rentaId, tipoNota) {
        document.querySelectorAll('.modal.show').forEach(m => {
            bootstrap.Modal.getInstance(m)?.hide();
        });

        const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalPrefacturaPago'));
        modal.show();

        const form = document.getElementById('form-pago-prefactura-pago');
        form.reset();
        form.dataset.rentaId = rentaId;

        // Selecciona el tipo de prefactura y permite elegir
        const tipoSelect = document.getElementById('tipo_prefactura_pago');
        if (tipoSelect) {
            tipoSelect.value = tipoNota;
            tipoSelect.disabled = false;
        }

        document.getElementById('prefactura-detalle-pago').innerHTML = '<div class="text-center text-muted">Cargando...</div>';
        
        // Resetear los campos de totales con validación
        const totalEl = document.getElementById('pago-total-pago');
        const subtotalEl = document.getElementById('prefactura-subtotal');
        const ivaEl = document.getElementById('prefactura-iva');
        
        if (totalEl) totalEl.textContent = '0.00';
        if (subtotalEl) subtotalEl.textContent = '0.00';
        if (ivaEl) ivaEl.textContent = '0.00';

        // Reiniciar campos de pago
        const metodoPago = document.getElementById('metodo-pago-pago');
        const efectivo = document.getElementById('pago-efectivo-pago');
        const seguimiento = document.getElementById('pago-seguimiento-pago');
        const montoRecibido = document.getElementById('monto-recibido-pago');
        const cambio = document.getElementById('cambio-pago');
        const numSeguimiento = document.getElementById('numero-seguimiento-pago');
        const btnGenerar = document.getElementById('btn-generar-pago-pago');
        const facturable = document.getElementById('facturable');
        const montoExacto = document.getElementById('monto-exacto-pago');

        metodoPago.value = '';
        efectivo.style.display = 'none';
        seguimiento.style.display = 'none';
        montoRecibido.value = '';
        cambio.textContent = '0.00';
        numSeguimiento.value = '';
        btnGenerar.style.display = '';
        facturable.value = '';
        if (montoExacto) montoExacto.value = '';
        
        // Ocultar info de saldo
        document.getElementById('info-saldo').style.display = 'none';

        // Cargar datos de prefactura y abonos
        Promise.all([
            fetch(`/prefactura/${rentaId}`).then(resp => resp.json()),
            fetch(`/prefactura/api/pagos/${rentaId}`).then(resp => resp.json()),
            fetch(`/prefactura/api/info-redondeo/${rentaId}`).then(resp => resp.json())
        ]).then(([data, pagos, infoRedondeo]) => {
            let html = `
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th>Cantidad</th>
                            <th>Días</th>
                            <th>Costo unitario</th>
                            <th>Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            data.detalle.forEach(item => {
                html += `
                    <tr>
                        <td>${item.nombre}</td>
                        <td>${item.cantidad}</td>
                        <td>${item.dias_renta}</td>
                        <td>$${parseFloat(item.costo_unitario).toFixed(2)}</td>
                        <td>$${parseFloat(item.subtotal).toFixed(2)}</td>
                    </tr>
                `;
            });
            html += `</tbody></table>`;

            // Calcular totales siguiendo la lógica exacta del backend
            let subtotalProductos = 0;
            data.detalle.forEach(item => {
                subtotalProductos += Math.round((parseFloat(item.subtotal) || 0) * 100) / 100;
            });

            // El costo de traslado se agrega al total antes de calcular IVA (lógica del backend)
            const costoTraslado = Math.round((parseFloat(data.costo_traslado) || 0) * 100) / 100;
            const totalSinIva = Math.round((subtotalProductos + costoTraslado) * 100) / 100;

            let trasladoHtml = '';
            if (costoTraslado > 0) {
                trasladoHtml = `<tr>
                    <td>Traslado <span class="text-muted">(${data.traslado})</span></td>
                    <td colspan="4" class="text-end">$${costoTraslado.toFixed(2)}</td>
                </tr>`;
            }

            // Usar el total con IVA del backend y calcular el IVA como diferencia
            const totalConIva = Math.round((parseFloat(data.total_con_iva) || 0) * 100) / 100;
            const iva = Math.round((totalConIva - totalSinIva) * 100) / 100;

            html += `
                <table class="table table-sm">
                    <tr>
                        <td>Subtotal</td>
                        <td colspan="4" class="text-end">$${subtotalProductos.toFixed(2)}</td>
                    </tr>
                    ${trasladoHtml}
                    <tr>
                        <td>+IVA (16%)</td>
                        <td colspan="4" class="text-end">$${iva.toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td><strong>Total</strong></td>
                        <td colspan="4" class="text-end"><strong>$${totalConIva.toFixed(2)}</strong></td>
                    </tr>
                </table>
            `;

            // Mostrar historial de pagos/abonos
            let totalAbonado = 0;
            let pagosHtml = '';
            if (pagos && pagos.length > 0) {
                pagosHtml += `<div class="mt-2"><strong>Historial de pagos:</strong></div>`;
                pagosHtml += `<table class="table table-sm table-bordered"><thead><tr><th>Folio</th><th>Tipo</th><th>Método</th><th>Monto</th><th>Fecha</th><th>PDF</th></tr></thead><tbody>`;
                pagos.forEach(p => {
                    totalAbonado += parseFloat(p.monto) || 0;
                    pagosHtml += `<tr>
                        <td>${p.id}</td>
                        <td>${p.tipo}</td>
                        <td>${p.metodo_pago}</td>
                        <td>$${parseFloat(p.monto).toFixed(2)}</td>
                        <td>${p.fecha_emision}</td>
                        <td><a href="/prefactura/pdf/${p.id}" target="_blank">PDF</a></td>
                    </tr>`;
                });
                pagosHtml += `</tbody></table>`;
            }
            const saldoPendiente = parseFloat(infoRedondeo.saldo_pendiente) || 0;
            const totalPagado = parseFloat(infoRedondeo.total_pagado) || 0;
            html += `<div class="mt-2"><strong>Total abonado:</strong> $${totalPagado.toFixed(2)}<br><strong>Saldo pendiente:</strong> $${saldoPendiente.toFixed(2)}</div>`;
            html += pagosHtml;

            document.getElementById('prefactura-detalle-pago').innerHTML = html;

            // Actualizar los elementos de totales en el modal
            const subtotalEl = document.getElementById('prefactura-subtotal');
            const ivaEl = document.getElementById('prefactura-iva');
            const totalEl = document.getElementById('pago-total-pago');
            
            // El subtotal del modal muestra solo productos (sin traslado)
            // El IVA se calcula sobre productos + traslado
            // El total es el total con IVA completo
            if (subtotalEl) subtotalEl.textContent = subtotalProductos.toFixed(2);
            if (ivaEl) ivaEl.textContent = iva.toFixed(2);
            if (totalEl) totalEl.textContent = totalConIva.toFixed(2);

            // Lógica para mostrar el monto correcto según tipo de prefactura
            function actualizarMontoPagar() {
                const tipo = tipoSelect.value;
                const infoSaldo = document.getElementById('info-saldo');
                const montoExactoInput = document.getElementById('monto-exacto-input');
                const montoExactoDisplay = document.getElementById('monto-exacto-display');
                const montoExactoHelp = document.getElementById('monto-exacto-help');
                
                if (tipo === 'abono') {
                    // Para abonos, mostrar siempre el saldo pendiente real
                    infoSaldo.style.display = '';
                    // Redondear saldo pendiente a 2 decimales para evitar errores de precisión
                    let saldoRedondeado = Math.round(saldoPendiente * 100) / 100;
                    if (saldoRedondeado < 0.01) saldoRedondeado = 0;
                    document.getElementById('saldo-pendiente-display').textContent = saldoRedondeado.toFixed(2);
                    // Si el método es tarjeta/transferencia, permitir liquidar con centavos exactos
                    if (metodoPago.value && metodoPago.value !== 'EFECTIVO') {
                        montoExactoInput.style.display = '';
                        montoExactoDisplay.style.display = 'none';
                        montoExactoHelp.style.display = '';
                        montoExactoInput.value = saldoRedondeado.toFixed(2);
                        montoExactoInput.max = saldoRedondeado.toFixed(2);
                        document.getElementById('pago-total-pago').textContent = montoExactoInput.value;
                    } else {
                        document.getElementById('pago-total-pago').textContent = saldoRedondeado.toFixed(2);
                    }
                } else {
                    // Pago inicial: mostrar total completo de la renta
                    infoSaldo.style.display = 'none';
                    document.getElementById('pago-total-pago').textContent = totalConIva.toFixed(2);
                    
                    // Asegurar que el campo editable esté oculto
                    montoExactoInput.style.display = 'none';
                    montoExactoDisplay.style.display = '';
                    montoExactoHelp.style.display = 'none';
                }
                
                // Aplicar redondeo según el tipo y método (coincidiendo con lógica Python)
                if (metodoPago.value === 'EFECTIVO') {
                    if (tipo === 'inicial') {
                        // Pago inicial en efectivo: siempre redondear
                        const montoRedondeado = redondearEfectivo(parseFloat(document.getElementById('pago-total-pago').textContent));
                        document.getElementById('pago-total-pago').textContent = montoRedondeado.toFixed(2);
                    } else if (tipo === 'abono' && infoRedondeo.aplicar_redondeo_efectivo) {
                        // Abono en efectivo: redondear si es primer abono O si el primero fue efectivo
                        // Nota: el redondeo específico (saldo vs monto) se maneja en el backend según sea liquidación o parcial
                        const montoRedondeado = redondearEfectivo(saldoPendiente);
                        document.getElementById('pago-total-pago').textContent = montoRedondeado.toFixed(2);
                    }
                }
                
                document.getElementById('monto-exacto-display').textContent = document.getElementById('pago-total-pago').textContent;

                // Mantener los valores de subtotal e IVA actualizados
                const subtotalEl = document.getElementById('prefactura-subtotal');
                const ivaEl = document.getElementById('prefactura-iva');
                
                // El subtotal del modal muestra solo productos (sin traslado)
                if (subtotalEl) subtotalEl.textContent = subtotalProductos.toFixed(2);
                if (ivaEl) ivaEl.textContent = iva.toFixed(2);
            }

            tipoSelect.onchange = actualizarMontoPagar;
            actualizarMontoPagar();
            


            // Listeners para pago
            metodoPago.onchange = () => {
                const metodo = metodoPago.value;
                montoRecibido.value = '';
                cambio.textContent = '0.00';
                numSeguimiento.value = '';

                const montoExactoInput = document.getElementById('monto-exacto-input');
                const montoExactoDisplay = document.getElementById('monto-exacto-display');
                const montoExactoHelp = document.getElementById('monto-exacto-help');
                
                if (metodo === 'EFECTIVO') {
                    efectivo.style.display = '';
                    seguimiento.style.display = 'none';
                    montoExactoInput.style.display = 'none';
                    montoExactoDisplay.style.display = '';
                    montoExactoHelp.style.display = 'none';
                } else if (metodo) {
                    efectivo.style.display = 'none';
                    seguimiento.style.display = '';
                    // Para abonos con otros métodos, mostrar campo editable
                    if (tipoSelect.value === 'abono') {
                        montoExactoInput.style.display = '';
                        montoExactoDisplay.style.display = 'none';
                        montoExactoHelp.style.display = '';
                        montoExactoInput.value = saldoPendiente.toFixed(2);
                        montoExactoInput.max = saldoPendiente;
                    } else {
                        montoExactoInput.style.display = 'none';
                        montoExactoDisplay.style.display = '';
                        montoExactoHelp.style.display = 'none';
                    }
                } else {
                    efectivo.style.display = 'none';
                    seguimiento.style.display = 'none';
                    montoExactoInput.style.display = 'none';
                    montoExactoDisplay.style.display = '';
                    montoExactoHelp.style.display = 'none';
                }
                
                // Recalcular el monto después del cambio de método
                actualizarMontoPagar();
            };

            montoRecibido.oninput = () => {
                const recibido = parseFloat(montoRecibido.value) || 0;
                const tipo = tipoSelect.value;
                const totalPagar = parseFloat(document.getElementById('pago-total-pago').textContent) || 0;
                
                if (tipo === 'abono') {
                    // Para abonos, permitir hasta el doble del saldo para cambio
                    if (recibido > saldoPendiente * 2) {
                        montoRecibido.value = (saldoPendiente * 2).toFixed(2);
                        return;
                    }
                    
                    // Determinar el monto real a cobrar y el cambio (coincidiendo con lógica Python)
                    let montoCobrar, cambioCalculado;
                    if (recibido >= saldoPendiente) {
                        // Liquidación: cobrar según redondeo si aplica (primer abono efectivo O si primero fue efectivo)
                        if (metodoPago.value === 'EFECTIVO' && infoRedondeo.aplicar_redondeo_efectivo) {
                            montoCobrar = redondearEfectivo(saldoPendiente);
                        } else {
                            montoCobrar = saldoPendiente;
                        }
                        cambioCalculado = recibido - montoCobrar;
                        
                        const ayudaTexto = document.querySelector('#info-saldo .text-info, #info-saldo .text-success');
                        if (ayudaTexto) {
                            ayudaTexto.textContent = '✓ Liquidando saldo completo - se calculará cambio si aplica';
                            ayudaTexto.className = 'text-success d-block';
                        }
                    } else {
                        // Abono parcial: en efectivo redondear si aplica, en otros métodos cobrar exacto
                        if (metodoPago.value === 'EFECTIVO' && infoRedondeo.aplicar_redondeo_efectivo) {
                            montoCobrar = redondearEfectivo(recibido);
                        } else {
                            montoCobrar = recibido;
                        }
                        cambioCalculado = 0;
                        
                        const ayudaTexto = document.querySelector('#info-saldo .text-success, #info-saldo .text-info');
                        if (ayudaTexto) {
                            ayudaTexto.textContent = 'Abono parcial - no se genera cambio';
                            ayudaTexto.className = 'text-info d-block';
                        }
                    }
                    
                    document.getElementById('pago-total-pago').textContent = montoCobrar.toFixed(2);
                    cambio.textContent = cambioCalculado > 0 ? cambioCalculado.toFixed(2) : '0.00';
                } else {
                    // Pago inicial: comportamiento normal
                    const calcCambio = recibido - totalPagar;
                    cambio.textContent = calcCambio > 0 ? calcCambio.toFixed(2) : '0.00';
                }
            };

            // Listener para el campo editable de monto exacto (abonos con tarjeta/transferencia)
            const montoExactoInput = document.getElementById('monto-exacto-input');
            montoExactoInput.addEventListener('input', function() {
                const tipo = tipoSelect.value;
                if (tipo === 'abono' && metodoPago.value !== 'EFECTIVO') {
                    const montoAbono = parseFloat(this.value) || 0;
                    const maxAbono = parseFloat(this.max) || saldoPendiente;
                    if (montoAbono > maxAbono) {
                        this.value = maxAbono.toFixed(2);
                    }
                    const montoFinal = parseFloat(this.value) || 0;
                    document.getElementById('pago-total-pago').textContent = montoFinal.toFixed(2);
                }
            });

            // Validación para tarjetas/transferencia
            const validarPagoNoEfectivo = () => {
                const numSeg = numSeguimiento.value.trim();
                const tipo = tipoSelect.value;
                const totalPagar = parseFloat(document.getElementById('pago-total-pago').textContent) || 0;
                if (metodoPago.value !== 'EFECTIVO' && metodoPago.value !== '') {
                    document.getElementById('monto-exacto-display').textContent = totalPagar.toFixed(2);
                }
            };

            numSeguimiento.oninput = validarPagoNoEfectivo;
            if (montoExacto) {
                montoExacto.addEventListener('input', validarPagoNoEfectivo);
            }

            facturable.onchange = () => {
                // Ya no se condiciona el botón
            };

            function validarFormulario() {
                return true;
            }
        }).catch(err => {
            document.getElementById('prefactura-detalle-pago').innerHTML = '<div class="text-danger">Error al cargar la prefactura o abonos.</div>';
            console.error('Error al obtener prefactura o abonos:', err);
        });
    };

    // Mantén el listener para el botón manual (por si lo usas en otras partes)
    document.body.addEventListener('click', function (e) {
        const target = e.target.closest('.btn-prefactura');
        if (target) {
            e.preventDefault();
            const fechaEntrada = target.dataset.fechaEntrada;
            if (!fechaEntrada || fechaEntrada.toLowerCase() === 'indefinido' || fechaEntrada.toLowerCase() === 'none') {
                Swal.fire({
                    icon: 'warning',
                    title: 'No puedes generar la prefactura',
                    text: 'Debes registrar primero la fecha de entrada para esta renta con valor indefinido.'
                });
                return;
            }
            const rentaId = target.dataset.rentaId;
            // Por defecto, tipo "inicial" si no se especifica
            window.abrirModalPrefacturaPago(rentaId, "inicial");
        }
    });

    // Enviar prefactura/pago
    const form = document.getElementById('form-pago-prefactura-pago');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            const facturable = document.getElementById('facturable').value;
            const metodo = document.getElementById('metodo-pago-pago').value;

            if (!facturable) {
                Swal.fire('Error', 'Debes seleccionar si requiere facturación', 'error');
                return;
            }
            if (!metodo) {
                Swal.fire('Error', 'Debes seleccionar un método de pago', 'error');
                return;
            }

            if (metodo === 'EFECTIVO') {
                const montoRecibido = parseFloat(document.getElementById('monto-recibido-pago').value) || 0;
                const totalPagar = parseFloat(document.getElementById('pago-total-pago').textContent) || 0;
                if (montoRecibido < totalPagar) {
                    Swal.fire('Error', 'El monto recibido debe ser mayor o igual al total a pagar', 'error');
                    return;
                }
            } else {
                const numSeguimiento = document.getElementById('numero-seguimiento-pago').value.trim();
                if (!numSeguimiento) {
                    Swal.fire('Error', 'Debes ingresar el número de seguimiento', 'error');
                    return;
                }
            }

            const btn = document.getElementById('btn-generar-pago-pago');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Procesando...';
            }

            const rentaId = form.dataset.rentaId;
            const tipo = document.getElementById('tipo_prefactura_pago').value;
            const monto = parseFloat(document.getElementById('pago-total-pago').textContent) || 0;

            let montoRecibido, cambio, seguimiento;
            if (metodo === 'EFECTIVO') {
                montoRecibido = parseFloat(document.getElementById('monto-recibido-pago').value);
                cambio = parseFloat(document.getElementById('cambio-pago').textContent);
                seguimiento = null;
            } else {
                montoRecibido = monto;
                cambio = null;
                seguimiento = document.getElementById('numero-seguimiento-pago').value;
            }

            const datos = {
                tipo: tipo,
                metodo_pago: metodo,
                monto: monto,
                monto_recibido: montoRecibido,
                cambio: cambio || 0,
                numero_seguimiento: seguimiento || '',
                facturable: facturable === '1'
            };

            try {
                const res = await fetch(`/prefactura/pago/${rentaId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(datos)
                });

                const json = await res.json();
                if (json.success) {
                    bootstrap.Modal.getInstance(document.getElementById('modalPrefacturaPago')).hide();
                    Swal.fire({
                        title: 'Prefactura generada',
                        text: '¿Deseas imprimir la prefactura ahora?',
                        icon: 'success',
                        showCancelButton: true,
                        confirmButtonText: 'Sí, imprimir',
                        cancelButtonText: 'No'
                    }).then(result => {
                        if (result.isConfirmed) {
                            window.open(`/prefactura/pdf/${json.prefactura_id}`, '_blank');
                        }
                        window.location.reload();
                    });
                } else {
                    Swal.fire('Error', json.error || 'No se pudo registrar la prefactura', 'error');
                }
            } catch (err) {
                console.error('Error en el guardado:', err);
                Swal.fire('Error', 'Error al enviar los datos al servidor', 'error');
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = 'Generar pago';
                }
            }
        });
    }
});