// ========================================
// INVENTARIO - FUNCIONALIDAD PRINCIPAL
// ========================================

// Búsqueda en tabla principal
document.getElementById('buscadorSucursal').addEventListener('keyup', function () {
    var filtro = this.value.toLowerCase();
    var rows = document.querySelectorAll('.table-inventario tbody tr');
    rows.forEach(function (row) {
        var texto = row.innerText.toLowerCase();
        row.style.display = texto.includes(filtro) ? '' : 'none';
    });
});

// ========================================
// VARIABLES GLOBALES
// ========================================

let piezasReparacion = [];
let piezasFinalizarReparacion = [];
let piezasAltaEquipo = [];
let piezasMarcarDaniadas = [];

// ========================================
// MODAL DE REPARACIÓN POR LOTES - FUNCIONALIDAD
// ========================================

// Inicializar funcionalidad del modal de reparación por lotes
document.addEventListener('DOMContentLoaded', function () {
    // Modal de reparación por lotes
    const selectorPiezaReparacion = document.getElementById('selectorPiezaReparacion');
    const btnAgregarReparacion = document.getElementById('btnAgregarPiezaReparacion');
    const infoDivReparacion = document.getElementById('infoPiezaSeleccionadaReparacion');

    if (selectorPiezaReparacion) {
        selectorPiezaReparacion.addEventListener('change', function () {
            const option = this.options[this.selectedIndex];

            if (this.value) {
                const nombrePieza = option.dataset.nombre;
                const daniadas = parseInt(option.dataset.daniadas);

                document.getElementById('nombrePiezaInfoReparacion').textContent = nombrePieza;
                document.getElementById('daniadasPiezaInfoReparacion').textContent = daniadas;

                infoDivReparacion.style.display = 'block';
                btnAgregarReparacion.disabled = false;
            } else {
                infoDivReparacion.style.display = 'none';
                btnAgregarReparacion.disabled = true;
            }
        });
    }

    if (btnAgregarReparacion) {
        btnAgregarReparacion.addEventListener('click', function () {
            const selector = document.getElementById('selectorPiezaReparacion');
            const option = selector.options[selector.selectedIndex];

            if (!selector.value) {
                Swal.fire('Error', 'Selecciona un equipo primero', 'error');
                return;
            }

            const idPieza = selector.value;
            const nombrePieza = option.dataset.nombre;
            const daniadas = parseInt(option.dataset.daniadas);

            const yaExiste = piezasReparacion.find(p => p.id === idPieza);
            if (yaExiste) {
                Swal.fire('Error', 'Este equipo ya está agregado', 'error');
                return;
            }

            piezasReparacion.push({
                id: idPieza,
                nombre: nombrePieza,
                cantidad: 1,
                maxCantidad: daniadas
            });

            actualizarListaPiezasReparacion();
            actualizarResumenReparacion();

            selector.value = '';
            btnAgregarReparacion.disabled = true;
            infoDivReparacion.style.display = 'none';
        });
    }

    // Modal de finalizar reparaciones
    const selectorPiezaFinalizar = document.getElementById('selectorPiezaFinalizar');
    const btnAgregarFinalizar = document.getElementById('btnAgregarPiezaFinalizar');
    const infoDivFinalizar = document.getElementById('infoPiezaSeleccionadaFinalizar');

    if (selectorPiezaFinalizar) {
        selectorPiezaFinalizar.addEventListener('change', function () {
            const option = this.options[this.selectedIndex];

            if (this.value) {
                const nombrePieza = option.dataset.nombre;
                const enReparacion = parseInt(option.dataset.en_reparacion);

                document.getElementById('nombrePiezaInfoFinalizar').textContent = nombrePieza;
                document.getElementById('enReparacionPiezaInfo').textContent = enReparacion;

                infoDivFinalizar.style.display = 'block';
                btnAgregarFinalizar.disabled = false;
            } else {
                infoDivFinalizar.style.display = 'none';
                btnAgregarFinalizar.disabled = true;
            }
        });
    }

    if (btnAgregarFinalizar) {
        btnAgregarFinalizar.addEventListener('click', function () {
            const selector = document.getElementById('selectorPiezaFinalizar');
            const option = selector.options[selector.selectedIndex];

            if (!selector.value) {
                Swal.fire('Error', 'Selecciona un equipo primero', 'error');
                return;
            }

            const idPieza = selector.value;
            const nombrePieza = option.dataset.nombre;
            const enReparacion = parseInt(option.dataset.en_reparacion);

            const yaExiste = piezasFinalizarReparacion.find(p => p.id === idPieza);
            if (yaExiste) {
                Swal.fire('Error', 'Este equipo ya está agregado', 'error');
                return;
            }

            piezasFinalizarReparacion.push({
                id: idPieza,
                nombre: nombrePieza,
                cantidad: 1,
                maxCantidad: enReparacion
            });

            actualizarListaPiezasFinalizar();
            actualizarResumenFinalizar();

            selector.value = '';
            btnAgregarFinalizar.disabled = true;
            infoDivFinalizar.style.display = 'none';
        });
    }

    // Limpiar modales cuando se cierren
    const modalReparacion = document.getElementById('modalReparacionLote');
    if (modalReparacion) {
        modalReparacion.addEventListener('hidden.bs.modal', function () {
            piezasReparacion = [];
            document.getElementById('selectorPiezaReparacion').value = '';
            document.getElementById('btnAgregarPiezaReparacion').disabled = true;
            document.getElementById('infoPiezaSeleccionadaReparacion').style.display = 'none';
            document.getElementById('listaPiezasAgregadasReparacion').style.display = 'none';
            document.getElementById('resumenReparacionLote').style.display = 'none';
            document.getElementById('btnConfirmarReparacionLote').disabled = true;
            document.getElementById('observacionesReparacion').value = '';
        });
    }

    const modalFinalizar = document.getElementById('modalFinalizarReparaciones');
    if (modalFinalizar) {
        modalFinalizar.addEventListener('hidden.bs.modal', function () {
            piezasFinalizarReparacion = [];
            document.getElementById('selectorPiezaFinalizar').value = '';
            document.getElementById('btnAgregarPiezaFinalizar').disabled = true;
            document.getElementById('infoPiezaSeleccionadaFinalizar').style.display = 'none';
            document.getElementById('listaPiezasAgregadasFinalizar').style.display = 'none';
            document.getElementById('resumenFinalizarReparaciones').style.display = 'none';
            document.getElementById('btnConfirmarFinalizarReparaciones').disabled = true;
        });
    }

    // Envío de formularios
    const formReparacion = document.getElementById('formReparacionLote');
    if (formReparacion) {
        formReparacion.addEventListener('submit', function (e) {
            e.preventDefault();

            if (piezasReparacion.length === 0) {
                Swal.fire('Error', 'Debes agregar al menos un equipo', 'error');
                return;
            }

            const observaciones = document.getElementById('observacionesReparacion').value || '';

            const piezasData = piezasReparacion.map(pieza => ({
                id_pieza: pieza.id,
                cantidad: pieza.cantidad
            }));

            const reparacionData = {
                sucursal_id: window.sucursalData.id_sucursal,
                piezas: piezasData,
                observaciones: observaciones
            };

            const btnConfirmar = document.getElementById('btnConfirmarReparacionLote');
            const originalText = btnConfirmar.innerHTML;
            btnConfirmar.disabled = true;
            btnConfirmar.innerHTML = '<i class="bi bi-hourglass-split"></i> Enviando...';

            fetch('/inventario/reparacion-lote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(reparacionData)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            title: '¡Éxito!',
                            html: `${data.message}<br><br><strong>¿Deseas descargar el PDF de la nota de salida?</strong>`,
                            icon: 'success',
                            showCancelButton: true,
                            confirmButtonColor: '#28a745',
                            cancelButtonColor: '#6c757d',
                            confirmButtonText: 'Sí, descargar PDF',
                            cancelButtonText: 'Solo cerrar'
                        }).then((result) => {
                            if (result.isConfirmed && data.folio) {
                                window.open(`/inventario/pdf-transferencia-salida/${data.folio}`, '_blank');
                            }
                            window.location.reload();
                        });
                    } else {
                        Swal.fire('Error', data.error || 'Ocurrió un error', 'error');
                    }
                })
                .catch(error => {
                    Swal.fire('Error', 'Error de conexión', 'error');
                })
                .finally(() => {
                    btnConfirmar.disabled = false;
                    btnConfirmar.innerHTML = originalText;
                });
        });
    }

    const formFinalizar = document.getElementById('formFinalizarReparaciones');
    if (formFinalizar) {
        formFinalizar.addEventListener('submit', function (e) {
            e.preventDefault();

            if (piezasFinalizarReparacion.length === 0) {
                Swal.fire('Error', 'Debes agregar al menos un equipo', 'error');
                return;
            }

            const piezasData = piezasFinalizarReparacion.map(pieza => ({
                id_pieza: pieza.id,
                cantidad: pieza.cantidad
            }));

            const finalizarData = {
                sucursal_id: window.sucursalData.id_sucursal,
                piezas: piezasData
            };

            const btnConfirmar = document.getElementById('btnConfirmarFinalizarReparaciones');
            const originalText = btnConfirmar.innerHTML;
            btnConfirmar.disabled = true;
            btnConfirmar.innerHTML = '<i class="bi bi-hourglass-split"></i> Procesando...';

            fetch('/inventario/finalizar-reparaciones', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(finalizarData)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire('¡Éxito!', data.message, 'success').then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire('Error', data.error || 'Ocurrió un error', 'error');
                    }
                })
                .catch(error => {
                    Swal.fire('Error', 'Error de conexión', 'error');
                })
                .finally(() => {
                    btnConfirmar.disabled = false;
                    btnConfirmar.innerHTML = originalText;
                });
        });
    }

    // ========================================
    // FUNCIONES DE TRANSFERENCIA - FUNCIONALIDAD EXISTENTE
    // ========================================
    
    // Variables para transferencias
    let piezasAgregadas = [];

    // Manejar cambio de tipo de operación
    const radioMandar = document.getElementById('operacion_mandar');
    const radioRecibir = document.getElementById('operacion_recibir');
    const contenidoMandar = document.getElementById('contenido_mandar');
    const contenidoRecibir = document.getElementById('contenido_recibir');
    const btnConfirmar = document.getElementById('btnConfirmarTransferencia');
    const textoBoton = document.getElementById('textoBotonConfirmar');

    function cambiarTipoOperacion() {
        const tituloAgregarPiezas = document.getElementById('tituloAgregarPiezas');
        const labelSelectorPieza = document.getElementById('labelSelectorPieza');
        const tituloListaPiezas = document.getElementById('tituloListaPiezas');
        const selectorPieza = document.getElementById('selectorPieza');
        
        // Cambiar opciones del selector según operación
        const opcionesMandar = selectorPieza.querySelectorAll('.opcion-mandar');
        const opcionesRecibir = selectorPieza.querySelectorAll('.opcion-recibir');
        
        if (radioMandar.checked) {
            contenidoMandar.style.display = 'block';
            contenidoRecibir.style.display = 'none';
            btnConfirmar.className = 'btn btn-danger';
            btnConfirmar.innerHTML = '<i class="bi bi-box-arrow-right"></i> <span id="textoBotonConfirmar">Mandar Equipos</span>';
            
            // Cambiar textos para MANDAR
            tituloAgregarPiezas.innerHTML = '<i class="bi bi-box-arrow-right"></i> Piezas a Enviar';
            labelSelectorPieza.textContent = 'Seleccionar Pieza a Enviar:';
            tituloListaPiezas.innerHTML = '<i class="bi bi-box-arrow-right"></i> Piezas a Enviar';
            document.getElementById('tituloResumen').innerHTML = '<i class="bi bi-box-arrow-right"></i> Resumen de Envío';
            
            // Manejar validación required para MANDAR
            document.getElementById('id_sucursal_destino').required = true;
            document.getElementById('id_sucursal_origen_recibir').required = false;
            
            // Mostrar solo opciones de mandar
            opcionesMandar.forEach(opt => opt.style.display = '');
            opcionesRecibir.forEach(opt => opt.style.display = 'none');
            
        } else {
            contenidoMandar.style.display = 'none';
            contenidoRecibir.style.display = 'block';
            btnConfirmar.className = 'btn btn-success';
            btnConfirmar.innerHTML = '<i class="bi bi-box-arrow-in-down"></i> <span id="textoBotonConfirmar">Recibir Equipos</span>';
            
            // Cambiar textos para RECIBIR
            tituloAgregarPiezas.innerHTML = '<i class="bi bi-box-arrow-in-down"></i> Piezas a Recibir';
            labelSelectorPieza.textContent = 'Seleccionar Pieza que Llega:';
            tituloListaPiezas.innerHTML = '<i class="bi bi-box-arrow-in-down"></i> Piezas que Llegan';
            document.getElementById('tituloResumen').innerHTML = '<i class="bi bi-box-arrow-in-down"></i> Resumen de Recepción';
            
            // Manejar validación required para RECIBIR
            document.getElementById('id_sucursal_destino').required = false;
            document.getElementById('id_sucursal_origen_recibir').required = true;
            
            // Mostrar solo opciones de recibir
            opcionesMandar.forEach(opt => opt.style.display = 'none');
            opcionesRecibir.forEach(opt => opt.style.display = '');
        }
        
        // Resetear formulario
        piezasAgregadas = [];
        actualizarListaPiezas();
        actualizarResumenTransferencia();
        selectorPieza.value = '';
        document.getElementById('btnAgregarPieza').disabled = true;
        document.getElementById('infoPiezaSeleccionada').style.display = 'none';
    }

    radioMandar.addEventListener('change', cambiarTipoOperacion);
    radioRecibir.addEventListener('change', cambiarTipoOperacion);

    // Manejar selección de pieza
    const selectorPieza = document.getElementById('selectorPieza');
    const btnAgregar = document.getElementById('btnAgregarPieza');
    const infoDiv = document.getElementById('infoPiezaSeleccionada');

    // Event listener para el selector
    selectorPieza.addEventListener('change', function () {
        const option = this.options[this.selectedIndex];

        if (this.value) {
            const disponibles = parseInt(option.dataset.disponibles);
            const nombre = option.dataset.nombre;

            btnAgregar.disabled = false;

            // Mostrar información
            document.getElementById('nombrePiezaInfo').textContent = nombre;
            document.getElementById('disponiblesPiezaInfo').textContent = disponibles;
            infoDiv.style.display = 'block';
        } else {
            btnAgregar.disabled = true;
            infoDiv.style.display = 'none';
        }
    });

    // Event listener para el botón agregar
    btnAgregar.addEventListener('click', function () {
        const selector = document.getElementById('selectorPieza');
        const option = selector.options[selector.selectedIndex];

        if (!selector.value) {
            Swal.fire('Error', 'Debes seleccionar una pieza', 'error');
            return;
        }

        const idPieza = selector.value;
        const nombrePieza = option.dataset.nombre;
        const disponibles = parseInt(option.dataset.disponibles);

        // Verificar si ya está agregada
        const yaExiste = piezasAgregadas.find(p => p.id === idPieza);
        if (yaExiste) {
            Swal.fire('Error', 'Esta pieza ya está en la lista', 'warning');
            return;
        }

        // Agregar directamente con cantidad 1 (se puede ajustar en la tabla)
        piezasAgregadas.push({
            id: idPieza,
            nombre: nombrePieza,
            cantidad: 1, // Cantidad por defecto
            disponibles: disponibles
        });

        // Actualizar UI
        actualizarListaPiezas();
        actualizarResumenTransferencia();

        // Limpiar selector
        selector.value = '';
        btnAgregar.disabled = true;
        infoDiv.style.display = 'none';
    });

    // Limpiar modal cuando se cierre
    document.getElementById('modalTransferencia').addEventListener('hidden.bs.modal', function () {
        piezasAgregadas = [];
        document.getElementById('selectorPieza').value = '';
        document.getElementById('btnAgregarPieza').disabled = true;
        document.getElementById('infoPiezaSeleccionada').style.display = 'none';
        document.getElementById('listaPiezasAgregadas').style.display = 'none';
        document.getElementById('resumenTransferencia').style.display = 'none';
        document.getElementById('btnConfirmarTransferencia').disabled = true;
        document.getElementById('observaciones').value = '';
        
        // Resetear a modo MANDAR por defecto
        document.getElementById('operacion_mandar').checked = true;
        document.getElementById('id_sucursal_destino').value = '';
        document.getElementById('id_sucursal_origen_recibir').value = '';
        cambiarTipoOperacion();
    });

    // ========================================
    // FORMULARIO DE TRANSFERENCIA - SUBMIT
    // ========================================
    
    document.getElementById('formTransferencia').addEventListener('submit', function (e) {
        e.preventDefault();

        // Determinar tipo de operación y datos según el modo
        const esEnvio = document.getElementById('operacion_mandar').checked;

        if (piezasAgregadas.length === 0) {
            const textoError = esEnvio ? 'Debes agregar al menos una pieza para enviar' : 'Debes agregar al menos una pieza para recibir';
            Swal.fire('Error', textoError, 'error');
            return;
        }
        let sucursalOrigenId, sucursalDestinoId, endpoint;

        if (esEnvio) {
            // Modo ENVIAR
            sucursalOrigenId = document.getElementById('id_sucursal_origen').value;
            sucursalDestinoId = document.getElementById('id_sucursal_destino').value;
            endpoint = '/inventario/enviar-equipos';
            
            if (!sucursalDestinoId) {
                Swal.fire('Error', 'Debes seleccionar la sucursal destino', 'error');
                return;
            }
        } else {
            // Modo RECIBIR
            sucursalOrigenId = document.getElementById('id_sucursal_origen_recibir').value;
            sucursalDestinoId = document.getElementById('id_sucursal_destino_recibir').value;
            endpoint = '/inventario/recibir-equipos';
            
            if (!sucursalOrigenId) {
                Swal.fire('Error', 'Debes seleccionar la sucursal de origen', 'error');
                return;
            }
        }

        const observaciones = document.getElementById('observaciones').value || '';

        // Preparar datos para JSON
        const piezasData = piezasAgregadas.map(pieza => ({
            id_pieza: pieza.id,
            cantidad: pieza.cantidad
        }));

        const transferData = {
            sucursal_origen_id: sucursalOrigenId,
            sucursal_destino_id: sucursalDestinoId,
            piezas: piezasData,
            observaciones: observaciones
        };

        // Deshabilitar botón y mostrar loading
        const btnConfirmar = document.getElementById('btnConfirmarTransferencia');
        const originalText = btnConfirmar.innerHTML;
        btnConfirmar.disabled = true;
        
        if (esEnvio) {
            btnConfirmar.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Enviando...';
        } else {
            btnConfirmar.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Recibiendo...';
        }

        // Enviar con AJAX a la ruta correcta
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(transferData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Cerrar modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalTransferencia'));
                    modal.hide();

                    // Mostrar éxito según el tipo de operación
                    let tituloExito, contenidoHTML;
                    
                    if (esEnvio) {
                        tituloExito = '¡Envío Exitoso!';
                        contenidoHTML = `
                            <div class="text-start">
                                <p><strong>${data.message}</strong></p>
                                <hr>
                                <p><strong>📋 Nota generada:</strong></p>
                                <div class="bg-light p-3 rounded mb-3">
                                    <p class="mb-0"><strong>Nota de Salida:</strong> #${data.folio_salida}</p>
                                </div>
                                <div class="d-grid gap-2">
                                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="descargarPDFTransferencia('${data.folio_salida}')">
                                        <i class="bi bi-file-earmark-pdf"></i> Descargar PDF Nota de Salida
                                    </button>
                                </div>
                                <small class="text-muted mt-2 d-block">Los folios son consecutivos por sucursal</small>
                            </div>
                        `;
                    } else {
                        tituloExito = '¡Recepción Exitosa!';
                        contenidoHTML = `
                            <div class="text-start">
                                <p><strong>${data.message}</strong></p>
                                <hr>
                                <p><strong>📋 Nota generada:</strong></p>
                                <div class="bg-light p-3 rounded mb-3">
                                    <p class="mb-0"><strong>Nota de Entrada:</strong> #${data.folio_entrada}</p>
                                </div>
                                <div class="d-grid gap-2">
                                    <button type="button" class="btn btn-outline-success btn-sm" onclick="descargarPDFRecepcion('${data.folio_entrada}')">
                                        <i class="bi bi-file-earmark-pdf"></i> Descargar PDF Nota de Entrada
                                    </button>
                                </div>
                                <small class="text-muted mt-2 d-block">Los folios son consecutivos por sucursal</small>
                            </div>
                        `;
                    }

                    Swal.fire({
                        title: tituloExito,
                        html: contenidoHTML,
                        icon: 'success',
                        confirmButtonText: 'Entendido',
                        width: '500px'
                    }).then(() => {
                        // Recargar página para mostrar inventario actualizado
                        window.location.reload();
                    });
            } else {
                Swal.fire('Error', data.error || 'Error al realizar la transferencia', 'error');
            }
            })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire('Error', 'Error de conexión al servidor', 'error');
        })
        .finally(() => {
            // Restaurar botón
            btnConfirmar.disabled = false;
            btnConfirmar.innerHTML = originalText;
        });
    });
    
    // ========================================
    // MODAL DE ALTA DE EQUIPO NUEVO
    // ========================================

    // Event listeners para modal de alta de equipo
    const selectorPiezaAlta = document.getElementById('selectorPiezaAlta');
    const btnAgregarAlta = document.getElementById('btnAgregarPiezaAlta');
    const infoDivAlta = document.getElementById('infoPiezaSeleccionadaAlta');

    if (selectorPiezaAlta) {
        selectorPiezaAlta.addEventListener('change', function () {
            const option = this.options[this.selectedIndex];

            if (this.value) {
                const nombre = option.dataset.nombre;
                const categoria = option.dataset.categoria || 'Sin categoría';

                btnAgregarAlta.disabled = false;

                // Mostrar información
                document.getElementById('nombrePiezaInfoAlta').textContent = nombre;
                document.getElementById('categoriaPiezaInfoAlta').textContent = categoria;
                infoDivAlta.style.display = 'block';
            } else {
                btnAgregarAlta.disabled = true;
                infoDivAlta.style.display = 'none';
            }
        });
    }

    if (btnAgregarAlta) {
        btnAgregarAlta.addEventListener('click', function () {
            const selector = document.getElementById('selectorPiezaAlta');
            const option = selector.options[selector.selectedIndex];

            if (!selector.value) {
                Swal.fire('Error', 'Debes seleccionar una pieza', 'error');
                return;
            }

            const idPieza = selector.value;
            const nombrePieza = option.dataset.nombre;
            const categoria = option.dataset.categoria || 'Sin categoría';

            const yaExiste = piezasAltaEquipo.find(p => p.id === idPieza);
            if (yaExiste) {
                Swal.fire('Error', 'Esta pieza ya está en la lista', 'warning');
                return;
            }

            piezasAltaEquipo.push({
                id: idPieza,
                nombre: nombrePieza,
                categoria: categoria,
                cantidad: 1
            });

            actualizarListaPiezasAlta();
            actualizarResumenAltaEquipo();

            selector.value = '';
            btnAgregarAlta.disabled = true;
            infoDivAlta.style.display = 'none';
        });
    }

    // Limpiar modal cuando se cierre
    const modalAltaEquipo = document.getElementById('modalAltaEquipoNuevo');
    if (modalAltaEquipo) {
        modalAltaEquipo.addEventListener('hidden.bs.modal', function () {
            piezasAltaEquipo = [];
            document.getElementById('selectorPiezaAlta').value = '';
            document.getElementById('btnAgregarPiezaAlta').disabled = true;
            document.getElementById('infoPiezaSeleccionadaAlta').style.display = 'none';
            document.getElementById('listaPiezasAgregadasAlta').style.display = 'none';
            document.getElementById('resumenAltaEquipo').style.display = 'none';
            document.getElementById('btnConfirmarAltaEquipo').disabled = true;
            document.getElementById('observacionesAlta').value = '';
        });
    }

    // Event listener para el formulario de alta
    const formAltaEquipo = document.getElementById('formAltaEquipoNuevo');
    if (formAltaEquipo) {
        formAltaEquipo.addEventListener('submit', function (e) {
            e.preventDefault();

            if (piezasAltaEquipo.length === 0) {
                Swal.fire('Error', 'Debes agregar al menos una pieza', 'error');
                return;
            }

            // Validación de permisos (si está definida la variable global)
            if (typeof window.userData !== 'undefined') {
                const sucursalId = window.sucursalData?.id_sucursal;
                
                if (window.userData.rol_id !== 1 && window.userData.sucursal_id !== sucursalId) {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Sin permisos',
                        text: 'Solo puedes realizar altas de equipo en tu sucursal asignada.',
                        confirmButtonText: 'Entendido'
                    });
                    return;
                }
            }

            const observaciones = document.getElementById('observacionesAlta').value || '';

            const piezasData = piezasAltaEquipo.map(pieza => ({
                id_pieza: pieza.id,
                cantidad: pieza.cantidad
            }));

            const altaData = {
                id_sucursal: window.sucursalData?.id_sucursal,
                piezas: piezasData,
                observaciones: observaciones
            };

            const btnConfirmar = document.getElementById('btnConfirmarAltaEquipo');
            const originalText = btnConfirmar.innerHTML;
            btnConfirmar.disabled = true;
            btnConfirmar.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Procesando...';

            fetch('/inventario/alta-equipo-nuevo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(altaData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: '¡Éxito!',
                        html: `${data.message}<br><br><strong>¿Deseas descargar el PDF del alta?</strong>`,
                        icon: 'success',
                        showCancelButton: true,
                        confirmButtonColor: '#28a745',
                        cancelButtonColor: '#6c757d',
                        confirmButtonText: 'Sí, descargar PDF',
                        cancelButtonText: 'Solo cerrar'
                    }).then((result) => {
                        if (result.isConfirmed && data.folio) {
                            descargarPDFAltaEquipo(data.folio);
                        }
                        window.location.reload();
                    });
                } else {
                    Swal.fire('Error', data.error || 'Error al realizar el alta', 'error');
                }
            })
            .catch(error => {
                Swal.fire('Error', 'Error de conexión', 'error');
            })
            .finally(() => {
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = originalText;
            });
        });
    }
    
    // ========================================
    // MODAL DE MARCAR COMO DAÑADAS - FUNCIONALIDAD
    // ========================================
    
    // Event listeners para modal de marcar como dañadas
    const selectorPiezaDaniada = document.getElementById('selectorPiezaDaniada');
    const btnAgregarDaniada = document.getElementById('btnAgregarPiezaDaniada');
    const infoDivDaniada = document.getElementById('infoPiezaSeleccionadaDaniada');

    if (selectorPiezaDaniada) {
        selectorPiezaDaniada.addEventListener('change', function () {
            const option = this.options[this.selectedIndex];
            
            if (this.value) {
                const disponibles = parseInt(option.dataset.disponibles);
                document.getElementById('nombrePiezaDaniada').textContent = option.dataset.nombre;
                document.getElementById('disponiblesPiezaDaniada').textContent = disponibles;
                infoDivDaniada.style.display = 'block';
                btnAgregarDaniada.disabled = false;
            } else {
                infoDivDaniada.style.display = 'none';
                btnAgregarDaniada.disabled = true;
            }
        });
    }

    if (btnAgregarDaniada) {
        btnAgregarDaniada.addEventListener('click', function () {
            const selector = document.getElementById('selectorPiezaDaniada');
            const option = selector.options[selector.selectedIndex];

            if (!selector.value) {
                Swal.fire('Error', 'Debe seleccionar una pieza', 'error');
                return;
            }

            const idPieza = selector.value;
            const nombrePieza = option.dataset.nombre;
            const disponibles = parseInt(option.dataset.disponibles);

            // Verificar si ya está agregada
            const yaExiste = piezasMarcarDaniadas.find(p => p.id === idPieza);
            if (yaExiste) {
                Swal.fire('Información', 'Esta pieza ya está en la lista', 'info');
                return;
            }

            // Agregar a la lista
            piezasMarcarDaniadas.push({
                id: idPieza,
                nombre: nombrePieza,
                cantidad: 1,
                maxCantidad: disponibles
            });

            // Actualizar UI
            actualizarListaPiezasDaniadas();
            actualizarResumenMarcarDaniadas();

            // Limpiar selector
            selector.value = '';
            btnAgregarDaniada.disabled = true;
            infoDivDaniada.style.display = 'none';
        });
    }
    
    // Limpiar modal cuando se cierre
    const modalMarcarDaniadas = document.getElementById('modalMarcarDaniadas');
    if (modalMarcarDaniadas) {
        modalMarcarDaniadas.addEventListener('hidden.bs.modal', function () {
            piezasMarcarDaniadas = [];
            document.getElementById('selectorPiezaDaniada').value = '';
            document.getElementById('btnAgregarPiezaDaniada').disabled = true;
            document.getElementById('infoPiezaSeleccionadaDaniada').style.display = 'none';
            document.getElementById('listaPiezasAgregadasDaniadas').style.display = 'none';
            document.getElementById('resumenMarcarDaniadas').style.display = 'none';
            document.getElementById('btnConfirmarMarcarDaniadas').disabled = true;
            document.getElementById('observacionesDaniada').value = '';
        });
    }
    
    // Event listener para el formulario de marcar como dañadas
    const formMarcarDaniadas = document.getElementById('formMarcarDaniadas');
    if (formMarcarDaniadas) {
        formMarcarDaniadas.addEventListener('submit', function (e) {
            e.preventDefault();
            
            if (piezasMarcarDaniadas.length === 0) {
                Swal.fire('Error', 'Debe agregar al menos una pieza para marcar como dañada', 'error');
                return;
            }
            
            const observaciones = document.getElementById('observacionesDaniada').value.trim();
            
            const data = {
                sucursal_id: window.sucursalData.id_sucursal,
                piezas: piezasMarcarDaniadas.map(p => ({
                    id_pieza: p.id,
                    cantidad: p.cantidad
                })),
                observaciones: observaciones
            };
            
            Swal.fire({
                title: '¿Confirmar marcado como dañadas?',
                text: `Se marcarán ${piezasMarcarDaniadas.length} tipo(s) de piezas como dañadas`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sí, marcar como dañadas',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Mostrar loading
                    Swal.fire({
                        title: 'Procesando...',
                        text: 'Marcando equipos como dañados',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });
                    
                    fetch('/inventario/marcar-daniadas', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.success) {
                            Swal.fire({
                                title: '¡Éxito!',
                                text: result.message,
                                icon: 'success',
                                confirmButtonText: 'Aceptar'
                            }).then(() => {
                                // Cerrar modal y recargar página
                                document.getElementById('modalMarcarDaniadas').querySelector('[data-bs-dismiss="modal"]').click();
                                location.reload();
                            });
                        } else {
                            Swal.fire('Error', result.error || 'Error al procesar la solicitud', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire('Error', 'Error de conexión al procesar la solicitud', 'error');
                    });
                }
            });
        });
    }
});

// ========================================
// FUNCIONES AUXILIARES DE TRANSFERENCIA
// ========================================

// Actualizar lista de piezas agregadas
function actualizarListaPiezasReparacion() {
    const lista = document.getElementById('listaPiezasAgregadasReparacion');
    const tabla = document.getElementById('tablaPiezasAgregadasReparacion');

    if (piezasReparacion.length === 0) {
        lista.style.display = 'none';
        return;
    }

    lista.style.display = 'block';

    let html = '';
    piezasReparacion.forEach((pieza, index) => {
        html += `
            <tr>
                <td>${pieza.nombre}</td>
                <td>
                    <input type="number" class="form-control form-control-sm" 
                           value="${pieza.cantidad}" min="1" max="${pieza.maxCantidad}"
                           onchange="actualizarCantidadPiezaReparacion(${index}, this.value)">
                </td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm" 
                            onclick="eliminarPiezaReparacion(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tabla.innerHTML = html;
}

// Actualizar cantidad de una pieza en reparación
function actualizarCantidadPiezaReparacion(index, nuevaCantidad) {
    const cantidad = parseInt(nuevaCantidad);
    const pieza = piezasReparacion[index];

    if (cantidad < 1 || cantidad > pieza.maxCantidad) {
        Swal.fire('Error', `La cantidad debe estar entre 1 y ${pieza.maxCantidad}`, 'error');
        actualizarListaPiezasReparacion(); // Reset
        return;
    }

    piezasReparacion[index].cantidad = cantidad;
    actualizarResumenReparacion();
}

// Eliminar pieza de la lista de reparación
function eliminarPiezaReparacion(index) {
    piezasReparacion.splice(index, 1);
    actualizarListaPiezasReparacion();
    actualizarResumenReparacion();
}

// Actualizar resumen de reparación
function actualizarResumenReparacion() {
    const resumenDiv = document.getElementById('resumenReparacionLote');
    const contenido = document.getElementById('resumenContenidoReparacion');
    const btnConfirmar = document.getElementById('btnConfirmarReparacionLote');

    if (piezasReparacion.length === 0) {
        resumenDiv.style.display = 'none';
        btnConfirmar.disabled = true;
        return;
    }

    resumenDiv.style.display = 'block';
    btnConfirmar.disabled = false;

    let html = '<ul class="list-unstyled mb-0">';
    piezasReparacion.forEach(pieza => {
        html += `<li><strong>${pieza.nombre}:</strong> ${pieza.cantidad} piezas</li>`;
    });
    html += '</ul>';

    contenido.innerHTML = html;
}

// Actualizar lista de piezas para finalizar
function actualizarListaPiezasFinalizar() {
    const lista = document.getElementById('listaPiezasAgregadasFinalizar');
    const tabla = document.getElementById('tablaPiezasAgregadasFinalizar');

    if (piezasFinalizarReparacion.length === 0) {
        lista.style.display = 'none';
        return;
    }

    lista.style.display = 'block';

    let html = '';
    piezasFinalizarReparacion.forEach((pieza, index) => {
        html += `
            <tr>
                <td>${pieza.nombre}</td>
                <td>
                    <input type="number" class="form-control form-control-sm" 
                           value="${pieza.cantidad}" min="1" max="${pieza.maxCantidad}"
                           onchange="actualizarCantidadPiezaFinalizar(${index}, this.value)">
                </td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm" 
                            onclick="eliminarPiezaFinalizar(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tabla.innerHTML = html;
}

// Actualizar cantidad de una pieza para finalizar
function actualizarCantidadPiezaFinalizar(index, nuevaCantidad) {
    const cantidad = parseInt(nuevaCantidad);
    const pieza = piezasFinalizarReparacion[index];

    if (cantidad < 1 || cantidad > pieza.maxCantidad) {
        Swal.fire('Error', `La cantidad debe estar entre 1 y ${pieza.maxCantidad}`, 'error');
        actualizarListaPiezasFinalizar(); // Reset
        return;
    }

    piezasFinalizarReparacion[index].cantidad = cantidad;
    actualizarResumenFinalizar();
}

// Eliminar pieza de la lista de finalizar
function eliminarPiezaFinalizar(index) {
    piezasFinalizarReparacion.splice(index, 1);
    actualizarListaPiezasFinalizar();
    actualizarResumenFinalizar();
}

// Actualizar resumen de finalizar
function actualizarResumenFinalizar() {
    const resumenDiv = document.getElementById('resumenFinalizarReparaciones');
    const contenido = document.getElementById('resumenContenidoFinalizar');
    const btnConfirmar = document.getElementById('btnConfirmarFinalizarReparaciones');

    if (piezasFinalizarReparacion.length === 0) {
        resumenDiv.style.display = 'none';
        btnConfirmar.disabled = true;
        return;
    }

    resumenDiv.style.display = 'block';
    btnConfirmar.disabled = false;

    let html = '<ul class="list-unstyled mb-0">';
    piezasFinalizarReparacion.forEach(pieza => {
        html += `<li><strong>${pieza.nombre}:</strong> ${pieza.cantidad} piezas</li>`;
    });
    html += '</ul>';

    contenido.innerHTML = html;
}

// Actualizar lista de piezas agregadas
function actualizarListaPiezas() {
    const lista = document.getElementById('listaPiezasAgregadas');
    const tabla = document.getElementById('tablaPiezasAgregadas');

    if (piezasAgregadas.length === 0) {
        lista.style.display = 'none';
        return;
    }

    lista.style.display = 'block';

    let html = '';
    piezasAgregadas.forEach((pieza, index) => {
        html += `
      <tr>
        <td>${pieza.nombre}</td>
        <td>
          <input type="number" class="form-control form-control-sm" 
                 value="${pieza.cantidad}" min="1" max="${pieza.disponibles}"
                 onchange="actualizarCantidadPieza(${index}, this.value)">
        </td>
        <td>
          <button type="button" class="btn btn-danger btn-sm" 
                  onclick="eliminarPieza(${index})">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      </tr>
    `;
    });

    tabla.innerHTML = html;
}

// Actualizar cantidad de una pieza
function actualizarCantidadPieza(index, nuevaCantidad) {
    const cantidad = parseInt(nuevaCantidad);
    const pieza = piezasAgregadas[index];

    if (cantidad < 1 || cantidad > pieza.disponibles) {
        Swal.fire('Error', `La cantidad debe estar entre 1 y ${pieza.disponibles}`, 'error');
        actualizarListaPiezas(); // Reset
        return;
    }

    piezasAgregadas[index].cantidad = cantidad;
    actualizarResumenTransferencia();
}

// Eliminar pieza de la lista
function eliminarPieza(index) {
    piezasAgregadas.splice(index, 1);
    actualizarListaPiezas();
    actualizarResumenTransferencia();
}

// Actualizar resumen de transferencia
function actualizarResumenTransferencia() {
    const resumenDiv = document.getElementById('resumenTransferencia');
    const contenido = document.getElementById('resumenContenido');
    const btnConfirmar = document.getElementById('btnConfirmarTransferencia');

    if (piezasAgregadas.length === 0) {
        resumenDiv.style.display = 'none';
        btnConfirmar.disabled = true;
        return;
    }

    resumenDiv.style.display = 'block';
    btnConfirmar.disabled = false;

    let html = '<ul class="list-unstyled mb-0">';
    piezasAgregadas.forEach(pieza => {
        html += `<li><strong>${pieza.nombre}:</strong> ${pieza.cantidad} piezas</li>`;
    });
    html += '</ul>';

    contenido.innerHTML = html;
}

// ========================================
// FUNCIONES DE DESCARGA PDF
// ========================================

// Función para descargar PDF de transferencia (envío)
function descargarPDFTransferencia(folio) {
    if (!folio) {
        Swal.fire('Error', 'Folio de transferencia no disponible', 'error');
        return;
    }
    
    // Abrir PDF en nueva ventana
    const url = `/inventario/pdf-transferencia-salida/${folio}`;
    window.open(url, '_blank');
}

// Función para descargar PDF de recepción
function descargarPDFRecepcion(folio) {
    if (!folio) {
        Swal.fire('Error', 'Folio de recepción no disponible', 'error');
        return;
    }
    
    // Abrir PDF en nueva ventana
    const url = `/inventario/pdf-transferencia-entrada/${folio}`;
    window.open(url, '_blank');
}

// Función para descargar PDF de alta de equipo
function descargarPDFAltaEquipo(folio) {
    if (!folio) {
        Swal.fire('Error', 'Folio de alta no disponible', 'error');
        return;
    }
    
    // Abrir PDF en nueva ventana
    const url = `/inventario/pdf-alta-equipo/${folio}`;
    window.open(url, '_blank');
}

// ========================================
// FUNCIONES AUXILIARES DE REPARACIÓN
// ========================================

// Actualizar lista de piezas para reparación
function actualizarListaPiezasReparacion() {
    const lista = document.getElementById('listaPiezasAgregadasReparacion');
    const tabla = document.getElementById('tablaPiezasAgregadasReparacion');

    if (piezasReparacion.length === 0) {
        lista.style.display = 'none';
        return;
    }

    lista.style.display = 'block';

    let html = '';
    piezasReparacion.forEach((pieza, index) => {
        html += `
            <tr>
                <td>${pieza.nombre}</td>
                <td>
                    <input type="number" class="form-control form-control-sm" 
                           value="${pieza.cantidad}" min="1" max="${pieza.maxCantidad}"
                           onchange="actualizarCantidadPiezaReparacion(${index}, this.value)">
                </td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm" 
                            onclick="eliminarPiezaReparacion(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tabla.innerHTML = html;
}

// Actualizar cantidad de una pieza en reparación
function actualizarCantidadPiezaReparacion(index, nuevaCantidad) {
    const cantidad = parseInt(nuevaCantidad);
    const pieza = piezasReparacion[index];

    if (cantidad < 1 || cantidad > pieza.maxCantidad) {
        Swal.fire('Error', `La cantidad debe estar entre 1 y ${pieza.maxCantidad}`, 'error');
        actualizarListaPiezasReparacion(); // Reset
        return;
    }

    piezasReparacion[index].cantidad = cantidad;
    actualizarResumenReparacion();
}

// Eliminar pieza de la lista de reparación
function eliminarPiezaReparacion(index) {
    piezasReparacion.splice(index, 1);
    actualizarListaPiezasReparacion();
    actualizarResumenReparacion();
}

// Actualizar resumen de reparación
function actualizarResumenReparacion() {
    const resumenDiv = document.getElementById('resumenReparacionLote');
    const contenido = document.getElementById('resumenContenidoReparacion');
    const btnConfirmar = document.getElementById('btnConfirmarReparacionLote');

    if (piezasReparacion.length === 0) {
        resumenDiv.style.display = 'none';
        btnConfirmar.disabled = true;
        return;
    }

    resumenDiv.style.display = 'block';
    btnConfirmar.disabled = false;

    let html = '<ul class="list-unstyled mb-0">';
    piezasReparacion.forEach(pieza => {
        html += `<li><strong>${pieza.nombre}:</strong> ${pieza.cantidad} piezas</li>`;
    });
    html += '</ul>';

    contenido.innerHTML = html;
}

// Actualizar lista de piezas para finalizar
function actualizarListaPiezasFinalizar() {
    const lista = document.getElementById('listaPiezasAgregadasFinalizar');
    const tabla = document.getElementById('tablaPiezasAgregadasFinalizar');

    if (piezasFinalizarReparacion.length === 0) {
        lista.style.display = 'none';
        return;
    }

    lista.style.display = 'block';

    let html = '';
    piezasFinalizarReparacion.forEach((pieza, index) => {
        html += `
            <tr>
                <td>${pieza.nombre}</td>
                <td>
                    <input type="number" class="form-control form-control-sm" 
                           value="${pieza.cantidad}" min="1" max="${pieza.maxCantidad}"
                           onchange="actualizarCantidadPiezaFinalizar(${index}, this.value)">
                </td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm" 
                            onclick="eliminarPiezaFinalizar(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tabla.innerHTML = html;
}

// Actualizar cantidad de una pieza para finalizar
function actualizarCantidadPiezaFinalizar(index, nuevaCantidad) {
    const cantidad = parseInt(nuevaCantidad);
    const pieza = piezasFinalizarReparacion[index];

    if (cantidad < 1 || cantidad > pieza.maxCantidad) {
        Swal.fire('Error', `La cantidad debe estar entre 1 y ${pieza.maxCantidad}`, 'error');
        actualizarListaPiezasFinalizar(); // Reset
        return;
    }

    piezasFinalizarReparacion[index].cantidad = cantidad;
    actualizarResumenFinalizar();
}

// Eliminar pieza de la lista de finalizar
function eliminarPiezaFinalizar(index) {
    piezasFinalizarReparacion.splice(index, 1);
    actualizarListaPiezasFinalizar();
    actualizarResumenFinalizar();
}

// Actualizar resumen de finalizar
function actualizarResumenFinalizar() {
    const resumenDiv = document.getElementById('resumenFinalizarReparaciones');
    const contenido = document.getElementById('resumenContenidoFinalizar');
    const btnConfirmar = document.getElementById('btnConfirmarFinalizarReparaciones');

    if (piezasFinalizarReparacion.length === 0) {
        resumenDiv.style.display = 'none';
        btnConfirmar.disabled = true;
        return;
    }

    resumenDiv.style.display = 'block';
    btnConfirmar.disabled = false;

    let html = '<ul class="list-unstyled mb-0">';
    piezasFinalizarReparacion.forEach(pieza => {
        html += `<li><strong>${pieza.nombre}:</strong> ${pieza.cantidad} piezas</li>`;
    });
    html += '</ul>';

    contenido.innerHTML = html;
}

// ========================================
// FUNCIONES AUXILIARES DE ALTA DE EQUIPO
// ========================================

// Actualizar lista de piezas para alta
function actualizarListaPiezasAlta() {
    const lista = document.getElementById('listaPiezasAgregadasAlta');
    const tabla = document.getElementById('tablaPiezasAgregadasAlta');

    if (piezasAltaEquipo.length === 0) {
        lista.style.display = 'none';
        return;
    }

    lista.style.display = 'block';

    let html = '';
    piezasAltaEquipo.forEach((pieza, index) => {
        html += `
            <tr>
                <td><strong>${pieza.nombre}</strong></td>
                <td><span class="badge bg-secondary">${pieza.categoria}</span></td>
                <td>
                    <input type="number" class="form-control form-control-sm" 
                           value="${pieza.cantidad}" min="1" max="999"
                           onchange="actualizarCantidadPiezaAlta(${index}, this.value)">
                </td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm" 
                            onclick="eliminarPiezaAlta(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tabla.innerHTML = html;
}

// Actualizar cantidad de una pieza en alta
function actualizarCantidadPiezaAlta(index, nuevaCantidad) {
    const cantidad = parseInt(nuevaCantidad);

    if (cantidad < 1 || cantidad > 999) {
        Swal.fire('Error', 'La cantidad debe estar entre 1 y 999', 'error');
        actualizarListaPiezasAlta(); // Reset
        return;
    }

    piezasAltaEquipo[index].cantidad = cantidad;
    actualizarResumenAltaEquipo();
}

// Eliminar pieza de la lista de alta
function eliminarPiezaAlta(index) {
    piezasAltaEquipo.splice(index, 1);
    actualizarListaPiezasAlta();
    actualizarResumenAltaEquipo();
}

// Actualizar resumen de alta de equipo
function actualizarResumenAltaEquipo() {
    const resumenDiv = document.getElementById('resumenAltaEquipo');
    const contenido = document.getElementById('resumenContenidoAlta');
    const btnConfirmar = document.getElementById('btnConfirmarAltaEquipo');

    if (piezasAltaEquipo.length === 0) {
        resumenDiv.style.display = 'none';
        btnConfirmar.disabled = true;
        return;
    }

    resumenDiv.style.display = 'block';
    btnConfirmar.disabled = false;

    const totalPiezas = piezasAltaEquipo.reduce((total, pieza) => total + pieza.cantidad, 0);

    let html = `
        <div class="row">
            <div class="col-md-6">
                <strong>Total de piezas diferentes:</strong> ${piezasAltaEquipo.length}
            </div>
            <div class="col-md-6">
                <strong>Cantidad total de equipos:</strong> ${totalPiezas}
            </div>
        </div>
        <hr>
        <strong>Detalle:</strong>
        <ul class="list-unstyled mb-0 mt-2">
    `;
    
    piezasAltaEquipo.forEach(pieza => {
        html += `<li><i class="bi bi-check-circle text-success me-1"></i><strong>${pieza.nombre}:</strong> ${pieza.cantidad} unidades</li>`;
    });
    
    html += '</ul>';

    contenido.innerHTML = html;
}

// ========================================
// FUNCIONES AUXILIARES DE MARCAR COMO DAÑADAS
// ========================================

// Actualizar lista de piezas para marcar como dañadas
function actualizarListaPiezasDaniadas() {
    const lista = document.getElementById('listaPiezasAgregadasDaniadas');
    const tabla = document.getElementById('tablaPiezasAgregadasDaniadas');

    if (piezasMarcarDaniadas.length === 0) {
        lista.style.display = 'none';
        return;
    }

    lista.style.display = 'block';

    let html = '';
    piezasMarcarDaniadas.forEach((pieza, index) => {
        html += `
            <tr>
                <td>${pieza.nombre}</td>
                <td>
                    <input type="number" class="form-control form-control-sm" 
                           value="${pieza.cantidad}" min="1" max="${pieza.maxCantidad}"
                           onchange="actualizarCantidadPiezaDaniada(${index}, this.value)" 
                           style="width: 70px;">
                </td>
                <td>
                    <button type="button" class="btn btn-sm btn-danger" 
                            onclick="eliminarPiezaDaniada(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tabla.innerHTML = html;
}

// Actualizar cantidad de una pieza a dañar
function actualizarCantidadPiezaDaniada(index, nuevaCantidad) {
    const cantidad = parseInt(nuevaCantidad);
    const pieza = piezasMarcarDaniadas[index];

    if (cantidad < 1 || cantidad > pieza.maxCantidad) {
        Swal.fire('Error', `La cantidad debe estar entre 1 y ${pieza.maxCantidad}`, 'error');
        return;
    }

    piezasMarcarDaniadas[index].cantidad = cantidad;
    actualizarResumenMarcarDaniadas();
}

// Eliminar pieza de la lista a dañar
function eliminarPiezaDaniada(index) {
    piezasMarcarDaniadas.splice(index, 1);
    actualizarListaPiezasDaniadas();
    actualizarResumenMarcarDaniadas();
}

// Actualizar resumen de marcar como dañadas
function actualizarResumenMarcarDaniadas() {
    const resumenDiv = document.getElementById('resumenMarcarDaniadas');
    const contenido = document.getElementById('resumenContenidoDaniadas');
    const btnConfirmar = document.getElementById('btnConfirmarMarcarDaniadas');

    if (piezasMarcarDaniadas.length === 0) {
        resumenDiv.style.display = 'none';
        btnConfirmar.disabled = true;
        return;
    }

    resumenDiv.style.display = 'block';
    btnConfirmar.disabled = false;

    let html = '<ul class="list-unstyled mb-0">';
    piezasMarcarDaniadas.forEach(pieza => {
        html += `<li><strong>${pieza.nombre}:</strong> ${pieza.cantidad} unidad${pieza.cantidad > 1 ? 'es' : ''}</li>`;
    });
    html += '</ul>';

    contenido.innerHTML = html;
}