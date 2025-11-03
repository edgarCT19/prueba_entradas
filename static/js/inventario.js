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
// FUNCIONES DE REPARACIÓN
// ========================================

// Confirmar envío a reparación
function confirmarEnvioReparacion(idPieza, nombrePieza, maxCantidad) {
    const cantidadInput = document.getElementById(`cantidad_reparacion_${idPieza}`);
    const cantidad = parseInt(cantidadInput.value);

    if (!cantidad || cantidad < 1) {
        Swal.fire('Error', 'Debes ingresar una cantidad válida', 'error');
        return;
    }

    if (cantidad > maxCantidad) {
        Swal.fire('Error', `No puedes enviar más de ${maxCantidad} piezas dañadas`, 'error');
        return;
    }

    Swal.fire({
        title: '¿Enviar a reparación?',
        html: `¿Estás seguro que deseas enviar <strong>${cantidad}</strong> ${cantidad === 1 ? 'pieza' : 'piezas'} de <strong>"${nombrePieza}"</strong> a reparación?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#ffc107',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, enviar a reparación',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            enviarAReparacion(idPieza, cantidad);
        }
    });
}

// Confirmar regreso a disponibles
function confirmarRegresarDisponible(idPieza, nombrePieza, maxCantidad) {
    const cantidadInput = document.getElementById(`cantidad_disponible_${idPieza}`);
    const cantidad = parseInt(cantidadInput.value);

    if (!cantidad || cantidad < 1) {
        Swal.fire('Error', 'Debes ingresar una cantidad válida', 'error');
        return;
    }

    if (cantidad > maxCantidad) {
        Swal.fire('Error', `No puedes regresar más de ${maxCantidad} piezas en reparación`, 'error');
        return;
    }

    Swal.fire({
        title: '¿Regresar a disponibles?',
        html: `¿Estás seguro que deseas regresar <strong>${cantidad}</strong> ${cantidad === 1 ? 'pieza' : 'piezas'} de <strong>"${nombrePieza}"</strong> a disponibles?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, regresar a disponibles',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            regresarADisponible(idPieza, cantidad);
        }
    });
}

// Enviar pieza a reparación
function enviarAReparacion(idPieza, cantidad) {
    const form = document.createElement('form');
    form.method = 'POST';
    
    // Crear la URL usando la variable global definida en el template
    form.action = window.inventarioRoutes.mandarAReparacion;

    const inputPieza = document.createElement('input');
    inputPieza.type = 'hidden';
    inputPieza.name = 'id_pieza';
    inputPieza.value = idPieza;

    const inputSucursal = document.createElement('input');
    inputSucursal.type = 'hidden';
    inputSucursal.name = 'id_sucursal';
    inputSucursal.value = window.sucursalData.id_sucursal;

    const inputCantidad = document.createElement('input');
    inputCantidad.type = 'hidden';
    inputCantidad.name = 'cantidad';
    inputCantidad.value = cantidad;

    form.appendChild(inputPieza);
    form.appendChild(inputSucursal);
    form.appendChild(inputCantidad);

    document.body.appendChild(form);
    form.submit();
}

// Regresar pieza a disponibles
function regresarADisponible(idPieza, cantidad) {
    const form = document.createElement('form');
    form.method = 'POST';
    
    // Crear la URL usando la variable global definida en el template
    form.action = window.inventarioRoutes.regresarADisponible;

    const inputPieza = document.createElement('input');
    inputPieza.type = 'hidden';
    inputPieza.name = 'id_pieza';
    inputPieza.value = idPieza;

    const inputSucursal = document.createElement('input');
    inputSucursal.type = 'hidden';
    inputSucursal.name = 'id_sucursal';
    inputSucursal.value = window.sucursalData.id_sucursal;

    const inputCantidad = document.createElement('input');
    inputCantidad.type = 'hidden';
    inputCantidad.name = 'cantidad';
    inputCantidad.value = cantidad;

    form.appendChild(inputPieza);
    form.appendChild(inputSucursal);
    form.appendChild(inputCantidad);

    document.body.appendChild(form);
    form.submit();
}

// ========================================
// MODAL DE TRANSFERENCIA - FUNCIONALIDAD
// ========================================

let piezasAgregadas = [];

// Manejar cambio de tipo de operación
document.addEventListener('DOMContentLoaded', function () {
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
});

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
// MODAL DE ALTA DE EQUIPO NUEVO
// ========================================

let piezasAltaEquipo = [];

// Inicializar funcionalidad del modal de alta de equipo
document.addEventListener('DOMContentLoaded', function () {
    const selectorPiezaAlta = document.getElementById('selectorPiezaAlta');
    const btnAgregarAlta = document.getElementById('btnAgregarPiezaAlta');
    const infoDivAlta = document.getElementById('infoPiezaSeleccionadaAlta');

    // Event listener para el selector de piezas
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

    // Event listener para agregar pieza
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

            // Verificar si ya está agregada
            const yaExiste = piezasAltaEquipo.find(p => p.id === idPieza);
            if (yaExiste) {
                Swal.fire('Error', 'Esta pieza ya está en la lista', 'warning');
                return;
            }

            // Agregar con cantidad por defecto de 1
            piezasAltaEquipo.push({
                id: idPieza,
                nombre: nombrePieza,
                categoria: categoria,
                cantidad: 1
            });

            // Actualizar UI
            actualizarListaPiezasAlta();
            actualizarResumenAltaEquipo();

            // Limpiar selector
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
                Swal.fire('Error', 'Debes agregar al menos una pieza para dar de alta', 'error');
                return;
            }

            // Validación adicional para empleados de sucursal
            const sucursalId = document.getElementById('id_sucursal_destino_alta').value;
            if (window.userData && window.userData.rol_id !== 2) { // Si no es admin
                if (parseInt(sucursalId) !== parseInt(window.userData.sucursal_id)) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Acceso Denegado',
                        text: 'Solo puedes realizar altas de equipo en tu sucursal asignada.',
                        confirmButtonText: 'Entendido'
                    });
                    return;
                }
            }

            const observaciones = document.getElementById('observacionesAlta').value || '';

            // Preparar datos
            const piezasData = piezasAltaEquipo.map(pieza => ({
                id_pieza: pieza.id,
                cantidad: pieza.cantidad
            }));

            const altaData = {
                sucursal_id: sucursalId,
                piezas: piezasData,
                observaciones: observaciones
            };

            // Deshabilitar botón y mostrar loading
            const btnConfirmar = document.getElementById('btnConfirmarAltaEquipo');
            const originalText = btnConfirmar.innerHTML;
            btnConfirmar.disabled = true;
            btnConfirmar.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Procesando...';

            // Llamada AJAX al backend
            console.log('Enviando datos:', altaData);
            
            fetch('/inventario/alta-equipo-nuevo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(altaData)
            })
            .then(response => {
                console.log('Respuesta recibida:', response);
                console.log('Response status:', response.status);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                return response.json();
            })
            .then(data => {
                console.log('Datos recibidos:', data);
                
                if (data.success) {
                    // Cerrar modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalAltaEquipoNuevo'));
                    modal.hide();

                    // Mostrar éxito con el mismo diseño que transferencias
                    const contenidoHTML = `
                        <div class="text-start">
                            <p><strong>${data.message}</strong></p>
                            <hr>
                            <p><strong>📋 Nota generada:</strong></p>
                            <div class="bg-light p-3 rounded mb-3">
                                <p class="mb-0"><strong>Nota de Entrada Alta:</strong> #${data.folio}</p>
                            </div>
                            <div class="d-grid gap-2">
                                <button type="button" class="btn btn-outline-success btn-sm" onclick="descargarPDFAltaEquipo('${data.folio}')">
                                    <i class="bi bi-file-earmark-pdf"></i> Descargar PDF Nota de Alta
                                </button>
                            </div>
                            <small class="text-muted mt-2 d-block">Los folios son consecutivos por sucursal</small>
                        </div>
                    `;

                    Swal.fire({
                        title: '¡Alta Exitosa!',
                        html: contenidoHTML,
                        icon: 'success',
                        confirmButtonText: 'Entendido',
                        width: '500px'
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire('Error', data.message, 'error');
                    btnConfirmar.disabled = false;
                    btnConfirmar.innerHTML = originalText;
                }
            })
            .catch(error => {
                console.error('Error completo:', error);
                Swal.fire('Error', 'Error de comunicación con el servidor: ' + error.message, 'error');
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = originalText;
            });
        });
    }
});

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