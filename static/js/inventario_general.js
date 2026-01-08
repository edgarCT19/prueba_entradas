// ========================================
// INVENTARIO GENERAL - FUNCIONALIDAD JAVASCRIPT
// ========================================

// Variables globales para inventario general
let piezasAgregadasGeneral = [];
let piezasAltaEquipoGeneral = [];

// Variables globales para gestión de equipos (alta/baja)
let equiposGestionGeneral = [];

// Variables globales para filtros
let filtroEstatusActual = 'todos';

// ========================================
// FUNCIONES DE FILTRADO POR ESTATUS
// ========================================

// Función para filtrar por estatus
function filtrarPorEstatus(estatus) {
  filtroEstatusActual = estatus;
  
  // Actualizar botones activos
  document.querySelectorAll('[id^="filtro-"]').forEach(btn => btn.classList.remove('active'));
  document.getElementById(`filtro-${estatus}`).classList.add('active');
  
  // Aplicar filtros
  aplicarFiltros();
}

// Función unificada para aplicar filtros
function aplicarFiltros() {
  const textoBusqueda = document.getElementById('buscadorPiezas').value.toLowerCase();
  const filas = document.querySelectorAll('.table-inventario tbody tr');
  
  filas.forEach(fila => {
    const estatusFila = fila.getAttribute('data-estatus') || 'activo';
    const textoFila = fila.textContent.toLowerCase();
    
    const coincideEstatus = filtroEstatusActual === 'todos' || estatusFila === filtroEstatusActual;
    const coincideTexto = textoFila.includes(textoBusqueda);
    
    fila.style.display = (coincideEstatus && coincideTexto) ? '' : 'none';
  });
}

// ========================================
// FUNCIONES DE GESTIÓN DE EQUIPOS
// ========================================

// Función para manejar el cambio de tipo de operación
function cambiarTipoOperacion() {
  const tipoOperacion = document.querySelector('input[name="tipoOperacion"]:checked');
  const seccionAlta = document.getElementById('contenidoPiezasAlta');
  const seccionBaja = document.getElementById('contenidoPiezasBaja');
  const motivoBajaDiv = document.getElementById('motivoBajaDiv');
  const observacionesTextarea = document.getElementById('observacionesAltaGeneral');
  const btnConfirmar = document.getElementById('btnConfirmarAltaEquipoGeneral');
  const iconoBoton = document.getElementById('iconoBotonConfirmar');
  const textoBoton = document.getElementById('textoBotonConfirmar');
  
  if (tipoOperacion && tipoOperacion.value === 'alta') {
    // Mostrar sección de alta
    seccionAlta.style.display = 'block';
    seccionBaja.style.display = 'none';
    motivoBajaDiv.style.display = 'none';
    
    // Cambiar textos para alta
    observacionesTextarea.placeholder = 'Ingresa observaciones sobre esta alta de equipos...';
    
    // Actualizar elementos dinámicos
    document.getElementById('tituloListaEquipos').textContent = 'Equipos a Registrar';
    document.getElementById('tituloResumenOperacion').textContent = 'Resumen del Alta';
    document.getElementById('cardListaEquipos').className = 'card border-success';
    document.getElementById('headerListaEquipos').className = 'card-header bg-success text-white';
    
    // Actualizar botón
    btnConfirmar.className = 'btn btn-success';
    iconoBoton.className = 'bi bi-plus-circle';
    textoBoton.textContent = 'Confirmar Alta';
    
  } else if (tipoOperacion && tipoOperacion.value === 'baja') {
    // Mostrar sección de baja
    seccionAlta.style.display = 'none';
    seccionBaja.style.display = 'block';
    motivoBajaDiv.style.display = 'block';
    
    // Cambiar textos para baja
    observacionesTextarea.placeholder = 'Ingresa observaciones sobre esta baja de equipos...';
    
    // Actualizar elementos dinámicos
    document.getElementById('tituloListaEquipos').textContent = 'Equipos a dar de Baja';
    document.getElementById('tituloResumenOperacion').textContent = 'Resumen de la Baja';
    document.getElementById('cardListaEquipos').className = 'card border-danger';
    document.getElementById('headerListaEquipos').className = 'card-header bg-danger text-white';
    
    // Actualizar botón
    btnConfirmar.className = 'btn btn-danger';
    iconoBoton.className = 'bi bi-dash-circle';
    textoBoton.textContent = 'Confirmar Baja';
    
    // Cargar equipos disponibles para baja si ya hay sucursal seleccionada
    cargarEquiposParaBaja();
  }
  
  // Limpiar formularios al cambiar
  limpiarFormulariosGestion();
  
  // Actualizar estado del botón
  actualizarEstadoBotonConfirmar();
}

// Función para limpiar formularios
function limpiarFormulariosGestion() {
  // Limpiar equipos agregados
  equiposGestionGeneral = [];
  actualizarListaEquiposGestionGeneral();
  
  // Limpiar campos
  document.getElementById('observacionesAltaGeneral').value = '';
  document.getElementById('motivoBaja').value = '';
  
  // Ocultar secciones
  document.getElementById('listaPiezasAgregadasAltaGeneral').style.display = 'none';
  document.getElementById('resumenAltaEquipoGeneral').style.display = 'none';
  
  // Resetear selects de alta
  const selectorAltaGeneral = document.getElementById('selectorPiezaAltaGeneral');
  if (selectorAltaGeneral) {
    selectorAltaGeneral.value = '';
  }
  
  // Ocultar info de pieza seleccionada
  document.getElementById('infoPiezaSeleccionadaAltaGeneral').style.display = 'none';
  
  // Resetear selects de baja
  document.getElementById('tipoEquipoBaja').innerHTML = '<option value="">Seleccionar equipo...</option>';
  document.getElementById('cantidadBaja').value = '1';
  document.getElementById('cantidadMaximaBaja').textContent = '0';
}

// Función para cargar equipos disponibles para baja
function cargarEquiposParaBaja() {
  const sucursalId = document.getElementById('id_sucursal_operacion_general').value;
  if (!sucursalId) {
    document.getElementById('tipoEquipoBaja').innerHTML = '<option value="">Primero selecciona una sucursal...</option>';
    return;
  }
  fetch(`/inventario/piezas-sucursal/${sucursalId}`)
    .then(response => response.json())
    .then(data => {
      const select = document.getElementById('tipoEquipoBaja');
      select.innerHTML = '<option value="">Seleccionar equipo...</option>';
      if (data.success && data.piezas.length > 0) {
        // Solo mostrar piezas con disponibles > 0
        let hayDisponibles = false;
        data.piezas.forEach(pieza => {
          if (pieza.disponibles > 0) {
            hayDisponibles = true;
            const option = document.createElement('option');
            option.value = pieza.id_pieza;
            option.textContent = `${pieza.nombre_pieza} (${pieza.categoria || '-'}) - Disponible: ${pieza.disponibles}`;
            option.dataset.cantidad = pieza.disponibles;
            option.dataset.categoria = pieza.categoria || '-';
            option.dataset.nombre = pieza.nombre_pieza;
            select.appendChild(option);
          }
        });
        if (!hayDisponibles) {
          select.innerHTML = '<option value="">No hay piezas disponibles en esta sucursal</option>';
        }
      } else {
        select.innerHTML = '<option value="">No hay piezas disponibles en esta sucursal</option>';
      }
    })
    .catch(error => {
      console.error('Error al cargar piezas:', error);
      Swal.fire('Error', 'No se pudieron cargar las piezas disponibles', 'error');
    });
}

// Función para actualizar cantidad máxima en baja
function actualizarCantidadMaximaBaja() {
  const select = document.getElementById('tipoEquipoBaja');
  const cantidadMaxima = document.getElementById('cantidadMaximaBaja');
  const cantidadInput = document.getElementById('cantidadBaja');
  
  if (select.value) {
    const option = select.options[select.selectedIndex];
    const cantidad = option.dataset.cantidad;
    cantidadMaxima.textContent = cantidad;
    cantidadInput.max = cantidad;
    cantidadInput.value = '1';
  } else {
    cantidadMaxima.textContent = '0';
    cantidadInput.max = '0';
    cantidadInput.value = '1';
  }
}

// Función actualizada para lista de equipos de gestión
function actualizarListaEquiposGestionGeneral() {
  const tabla = document.getElementById('tablaPiezasAgregadasAltaGeneral');
  const lista = document.getElementById('listaPiezasAgregadasAltaGeneral');
  
  tabla.innerHTML = '';
  
  if (equiposGestionGeneral.length === 0) {
    lista.style.display = 'none';
    actualizarEstadoBotonConfirmar();
    return;
  }
  
  lista.style.display = 'block';
  
  equiposGestionGeneral.forEach((equipo, index) => {
    const fila = document.createElement('tr');
    fila.innerHTML = `
      <td>${equipo.nombre}</td>
      <td>${equipo.categoria}</td>
      <td>${equipo.cantidad}</td>
      <td>
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="eliminarEquipoGestion(${index})">
          <i class="bi bi-trash"></i>
        </button>
      </td>
    `;
    tabla.appendChild(fila);
  });
  
  actualizarEstadoBotonConfirmar();
}

// Función para actualizar estado del botón de confirmación
function actualizarEstadoBotonConfirmar() {
  const btnConfirmar = document.getElementById('btnConfirmarAltaEquipoGeneral');
  const tipoOperacion = document.querySelector('input[name="tipoOperacion"]:checked')?.value;
  const motivoBaja = document.getElementById('motivoBaja').value;
  
  let habilitado = equiposGestionGeneral.length > 0;
  
  // Para bajas, también verificar que tenga motivo
  if (tipoOperacion === 'baja') {
    habilitado = habilitado && motivoBaja.trim() !== '';
  }
  
  btnConfirmar.disabled = !habilitado;
}

// Función para eliminar equipo de gestión
function eliminarEquipoGestion(index) {
  equiposGestionGeneral.splice(index, 1);
  actualizarListaEquiposGestionGeneral();
}

// Función para agregar equipo para alta
function agregarEquipoAlta() {
  const tipoSelect = document.getElementById('selectorPiezaAltaGeneral');
  
  if (!tipoSelect.value) {
    Swal.fire('Error', 'Por favor selecciona un tipo de equipo', 'error');
    return;
  }
  
  // Solicitar cantidad al usuario
  Swal.fire({
    title: 'Cantidad de equipos',
    text: '¿Cuántos equipos de este tipo quieres agregar?',
    input: 'number',
    inputValue: 1,
    inputAttributes: {
      min: 1,
      max: 999,
      step: 1
    },
    showCancelButton: true,
    confirmButtonText: 'Agregar',
    cancelButtonText: 'Cancelar',
    inputValidator: (value) => {
      const cantidad = parseInt(value);
      if (!value || cantidad < 1 || cantidad > 999) {
        return 'La cantidad debe ser entre 1 y 999';
      }
    }
  }).then((result) => {
    if (result.isConfirmed) {
      const cantidad = parseInt(result.value);
      const tipoOption = tipoSelect.options[tipoSelect.selectedIndex];
      
      const equipo = {
        id: parseInt(tipoSelect.value),
        nombre: tipoOption.dataset.nombre,
        categoria: tipoOption.dataset.categoria,
        cantidad: cantidad,
        tipo: 'alta'
      };
      
      // Verificar si ya existe
      const yaExiste = equiposGestionGeneral.find(e => e.id === equipo.id);
      if (yaExiste) {
        yaExiste.cantidad += cantidad;
      } else {
        equiposGestionGeneral.push(equipo);
      }
      
      actualizarListaEquiposGestionGeneral();
      
      // Limpiar selector
      tipoSelect.value = '';
      document.getElementById('infoPiezaSeleccionadaAltaGeneral').style.display = 'none';
    }
  });
}

// Función para agregar equipo para baja
function agregarEquipoBaja() {
  const tipoSelect = document.getElementById('tipoEquipoBaja');
  const cantidadInput = document.getElementById('cantidadBaja');
  
  if (!tipoSelect.value || !cantidadInput.value) {
    Swal.fire('Error', 'Por favor selecciona un equipo y cantidad', 'error');
    return;
  }
  
  const cantidad = parseInt(cantidadInput.value);
  const tipoOption = tipoSelect.options[tipoSelect.selectedIndex];
  const disponible = parseInt(tipoOption.dataset.cantidad);
  
  if (cantidad <= 0 || cantidad > disponible) {
    Swal.fire('Error', `La cantidad debe ser entre 1 y ${disponible}`, 'error');
    return;
  }
  
  const equipo = {
    id: parseInt(tipoSelect.value),
    nombre: tipoOption.dataset.nombre,
    categoria: tipoOption.dataset.categoria,
    cantidad: cantidad,
    disponible: disponible,
    tipo: 'baja'
  };
  
  // Verificar si ya existe
  const yaExiste = equiposGestionGeneral.find(e => e.id === equipo.id);
  if (yaExiste) {
    const nuevaCantidad = yaExiste.cantidad + cantidad;
    if (nuevaCantidad > disponible) {
      Swal.fire('Error', `No puedes dar de baja más de ${disponible} unidades de este equipo`, 'error');
      return;
    }
    yaExiste.cantidad = nuevaCantidad;
  } else {
    equiposGestionGeneral.push(equipo);
  }
  
  actualizarListaEquiposGestionGeneral();
  
  // Limpiar campos
  tipoSelect.value = '';
  cantidadInput.value = '1';
  document.getElementById('cantidadMaximaBaja').textContent = '0';
}

// Función para procesar gestión de equipos (alta o baja)
function procesarGestionEquipos() {
  const tipoOperacion = document.querySelector('input[name="tipoOperacion"]:checked')?.value;
  const observaciones = document.getElementById('observacionesAltaGeneral').value.trim();
  const motivoBaja = document.getElementById('motivoBaja').value;
  const sucursalId = document.getElementById('id_sucursal_operacion_general').value;
  
  // Validaciones
  if (!tipoOperacion) {
    Swal.fire('Error', 'Selecciona el tipo de operación', 'error');
    return;
  }
  
  if (!sucursalId) {
    Swal.fire('Error', 'Selecciona una sucursal', 'error');
    return;
  }
  
  if (equiposGestionGeneral.length === 0) {
    Swal.fire('Error', 'Agrega al menos un equipo', 'error');
    return;
  }
  
  if (tipoOperacion === 'baja' && !motivoBaja) {
    Swal.fire('Error', 'El motivo de baja es obligatorio', 'error');
    return;
  }
  
  // Mostrar confirmación
  const titulo = tipoOperacion === 'alta' ? 'Confirmar Alta de Equipos' : 'Confirmar Baja de Equipos';
  const texto = tipoOperacion === 'alta' 
    ? `¿Confirmas el alta de ${equiposGestionGeneral.length} tipo(s) de equipos?`
    : `¿Confirmas la baja de ${equiposGestionGeneral.length} tipo(s) de equipos? Esta acción no se puede deshacer.`;

  Swal.fire({
    title: titulo,
    text: texto,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: tipoOperacion === 'alta' ? '#198754' : '#dc3545',
    cancelButtonColor: '#6c757d',
    confirmButtonText: tipoOperacion === 'alta' ? 'Sí, dar de alta' : 'Sí, dar de baja',
    cancelButtonText: 'Cancelar'
  }).then((result) => {
    if (result.isConfirmed) {
      ejecutarGestionEquiposAltaBaja(tipoOperacion, sucursalId, equiposGestionGeneral, motivoBaja, observaciones);
    }
  });
}

// Nueva función para ejecutar la gestión de equipos usando el endpoint existente
function ejecutarGestionEquiposAltaBaja(tipoOperacion, sucursalId, equipos, motivoBaja, observaciones) {
  const btnConfirmar = document.getElementById('btnConfirmarAltaEquipoGeneral');
  btnConfirmar.disabled = true;
  btnConfirmar.innerHTML = '<i class="bi bi-hourglass-split"></i> Procesando...';

  // Procesar cada equipo individualmente (una petición por equipo)
  let exitos = 0;
  let errores = 0;
  let erroresMsg = [];
  let totalEquipos = equipos.length;
  let procesados = 0;

  equipos.forEach((equipo, idx) => {
    const formData = new FormData();
    formData.append('id_pieza', equipo.id);
    formData.append('id_sucursal', sucursalId);
    formData.append('cantidad', equipo.cantidad);
    formData.append('tipo', tipoOperacion);
    if (tipoOperacion === 'baja') {
      formData.append('descripcion', motivoBaja || '');
    }
    // Observaciones no se usa en backend actual, pero si se requiere, agregar aquí

    fetch('/inventario/alta_baja_pieza', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      // Si redirige, considerar como éxito
      if (response.redirected || response.status === 200) {
        exitos++;
      } else {
        errores++;
        erroresMsg.push(`Error en equipo: ${equipo.nombre}`);
      }
    })
    .catch(() => {
      errores++;
      erroresMsg.push(`Error en equipo: ${equipo.nombre}`);
    })
    .finally(() => {
      procesados++;
      if (procesados === totalEquipos) {
        // Mostrar resultado final
        if (exitos > 0) {
          Swal.fire({
            title: tipoOperacion === 'alta' ? '¡Alta de Equipos Exitosa!' : '¡Baja de Equipos Exitosa!',
            html: `<div class='text-start'>Se procesaron ${exitos} de ${totalEquipos} equipos correctamente.${errores > 0 ? '<br><br><b>Errores:</b><br>' + erroresMsg.join('<br>') : ''}</div>`,
            icon: 'success',
            confirmButtonText: 'Entendido',
            confirmButtonColor: '#0d6efd',
            allowOutsideClick: false
          }).then(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalAltaEquipoGeneral'));
            if (modal) modal.hide();
            window.location.reload();
          });
        } else {
          Swal.fire('Error', erroresMsg.join('<br>') || 'Error en la operación', 'error');
        }
        btnConfirmar.disabled = false;
        btnConfirmar.innerHTML = `<i class="bi bi-${tipoOperacion === 'alta' ? 'plus' : 'dash'}-circle"></i> Confirmar ${tipoOperacion === 'alta' ? 'Alta' : 'Baja'}`;
      }
    });
  });
}

// ========================================
// FUNCIONES DE TRANSFERENCIAS
// ========================================

// Función para cargar piezas de una sucursal específica
function cargarPiezasPorSucursal(sucursalId) {
    fetch(`/inventario/piezas-sucursal/${sucursalId}`)
        .then(response => response.json())
        .then(data => {
            const selector = document.getElementById('selectorPiezaGeneral');
            selector.innerHTML = '<option value="">Seleccionar pieza...</option>';
            
            if (data.success && data.piezas.length > 0) {
                data.piezas.forEach(pieza => {
                    if (pieza.disponibles > 0) {
                        const option = document.createElement('option');
                        option.value = pieza.id_pieza;
                        option.dataset.nombre = pieza.nombre_pieza;
                        option.dataset.disponibles = pieza.disponibles;
                        option.textContent = `${pieza.nombre_pieza} - ${pieza.disponibles} disponibles`;
                        selector.appendChild(option);
                    }
                });
                selector.disabled = false;
            } else {
                selector.innerHTML = '<option value="">No hay piezas disponibles en esta sucursal</option>';
                selector.disabled = true;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const selector = document.getElementById('selectorPiezaGeneral');
            selector.innerHTML = '<option value="">Error al cargar piezas</option>';
            selector.disabled = true;
        });
}

// Actualizar lista de piezas para inventario general
function actualizarListaPiezasGeneral() {
    const lista = document.getElementById('listaPiezasAgregadasGeneral');
    const tabla = document.getElementById('tablaPiezasAgregadasGeneral');

    if (piezasAgregadasGeneral.length === 0) {
        lista.style.display = 'none';
        return;
    }

    lista.style.display = 'block';

    let html = '';
    piezasAgregadasGeneral.forEach((pieza, index) => {
        html += `
            <tr>
                <td>${pieza.nombre}</td>
                <td>
                    <input type="number" class="form-control form-control-sm" 
                           value="${pieza.cantidad}" min="1" max="${pieza.disponibles}"
                           onchange="actualizarCantidadPiezaGeneral(${index}, this.value)">
                </td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm" 
                            onclick="eliminarPiezaGeneral(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tabla.innerHTML = html;
}

// Actualizar cantidad de una pieza en inventario general
function actualizarCantidadPiezaGeneral(index, nuevaCantidad) {
    const cantidad = parseInt(nuevaCantidad);
    const pieza = piezasAgregadasGeneral[index];

    if (cantidad < 1 || cantidad > pieza.disponibles) {
        Swal.fire('Error', `La cantidad debe estar entre 1 y ${pieza.disponibles}`, 'error');
        actualizarListaPiezasGeneral(); // Reset
        return;
    }

    piezasAgregadasGeneral[index].cantidad = cantidad;
    actualizarResumenTransferenciaGeneral();
}

// Eliminar pieza de la lista en inventario general
function eliminarPiezaGeneral(index) {
    piezasAgregadasGeneral.splice(index, 1);
    actualizarListaPiezasGeneral();
    actualizarResumenTransferenciaGeneral();
}

// Actualizar resumen de transferencia en inventario general
function actualizarResumenTransferenciaGeneral() {
    const resumenDiv = document.getElementById('resumenTransferenciaGeneral');
    const contenido = document.getElementById('resumenContenidoGeneral');
    const btnConfirmar = document.getElementById('btnConfirmarTransferenciaGeneral');

    if (piezasAgregadasGeneral.length === 0) {
        resumenDiv.style.display = 'none';
        btnConfirmar.disabled = true;
        return;
    }

    resumenDiv.style.display = 'block';
    btnConfirmar.disabled = false;

    let html = '<ul class="list-unstyled mb-0">';
    piezasAgregadasGeneral.forEach(pieza => {
        html += `<li><strong>${pieza.nombre}:</strong> ${pieza.cantidad} piezas</li>`;
    });
    html += '</ul>';

    contenido.innerHTML = html;
}

// Actualizar lista de piezas para alta general
function actualizarListaPiezasAltaGeneral() {
    const lista = document.getElementById('listaPiezasAgregadasAltaGeneral');
    const tabla = document.getElementById('tablaPiezasAgregadasAltaGeneral');

    if (piezasAltaEquipoGeneral.length === 0) {
        lista.style.display = 'none';
        return;
    }

    lista.style.display = 'block';

    let html = '';
    piezasAltaEquipoGeneral.forEach((pieza, index) => {
        html += `
            <tr>
                <td><strong>${pieza.nombre}</strong></td>
                <td><span class="badge bg-secondary">${pieza.categoria}</span></td>
                <td>
                    <input type="number" class="form-control form-control-sm" 
                           value="${pieza.cantidad}" min="1" max="999"
                           onchange="actualizarCantidadPiezaAltaGeneral(${index}, this.value)">
                </td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm" 
                            onclick="eliminarPiezaAltaGeneral(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tabla.innerHTML = html;
}

// Actualizar cantidad de una pieza en alta general
function actualizarCantidadPiezaAltaGeneral(index, nuevaCantidad) {
    const cantidad = parseInt(nuevaCantidad);

    if (cantidad < 1 || cantidad > 999) {
        Swal.fire('Error', 'La cantidad debe estar entre 1 y 999', 'error');
        actualizarListaPiezasAltaGeneral(); // Reset
        return;
    }

    piezasAltaEquipoGeneral[index].cantidad = cantidad;
    actualizarResumenAltaEquipoGeneral();
}

// Eliminar pieza de la lista de alta general
function eliminarPiezaAltaGeneral(index) {
    piezasAltaEquipoGeneral.splice(index, 1);
    actualizarListaPiezasAltaGeneral();
    actualizarResumenAltaEquipoGeneral();
}

// Actualizar resumen de alta de equipo general
function actualizarResumenAltaEquipoGeneral() {
    const resumenDiv = document.getElementById('resumenAltaEquipoGeneral');
    const contenido = document.getElementById('resumenContenidoAltaGeneral');
    const btnConfirmar = document.getElementById('btnConfirmarAltaEquipoGeneral');

    if (piezasAltaEquipoGeneral.length === 0) {
        resumenDiv.style.display = 'none';
        btnConfirmar.disabled = true;
        return;
    }

    resumenDiv.style.display = 'block';
    btnConfirmar.disabled = false;

    const totalEquipos = piezasAltaEquipoGeneral.reduce((total, pieza) => total + pieza.cantidad, 0);

    let html = `
        <div class="row">
            <div class="col-md-6">
                <strong>Tipos de equipos diferentes:</strong> ${piezasAltaEquipoGeneral.length}
            </div>
            <div class="col-md-6">
                <strong>Cantidad total de equipos:</strong> ${totalEquipos}
            </div>
        </div>
        <hr>
        <strong>Detalle:</strong>
        <ul class="list-unstyled mb-0 mt-2">
    `;
    
    piezasAltaEquipoGeneral.forEach(pieza => {
        html += `<li><i class="bi bi-check-circle text-success me-1"></i><strong>${pieza.nombre}:</strong> ${pieza.cantidad} unidades</li>`;
    });
    
    html += '</ul>';

    contenido.innerHTML = html;
}

// ========================================
// FUNCIONES DE DESCONTINUACIÓN DE PIEZAS
// ========================================

// Función para verificar productos asociados y descontinuar pieza
function verificarYDescontinuarPieza(idPieza, nombrePieza) {
  // Primero verificar si hay productos asociados
  fetch(`/inventario/verificar-productos-asociados/${idPieza}`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        if (data.total > 0) {
          // Hay productos asociados, mostrar alerta con lista
          let listaProductos = data.productos.map(producto => 
            `• ${producto.nombre} (${producto.tipo === 'conjunto' ? 'Kit' : 'Individual'}) - Cantidad: ${producto.cantidad}`
          ).join('<br>');
          
          Swal.fire({
            title: '⚠️ No se puede descontinuar',
            html: `
              <div class="text-start">
                <p>La pieza <strong>"${nombrePieza}"</strong> está asociada a los siguientes productos activos:</p>
                <div class="alert alert-warning text-start mt-3">
                  ${listaProductos}
                </div>
                <p class="mt-3">Para descontinuar esta pieza, primero debes:</p>
                <ol class="text-start">
                  <li>Ir a la sección de <strong>Productos</strong></li>
                  <li>Editar cada producto listado</li>
                  <li>Remover esta pieza de cada producto</li>
                  <li>O descontinuar los productos primero</li>
                </ol>
              </div>
            `,
            icon: 'warning',
            confirmButtonText: 'Ir a Productos',
            confirmButtonColor: '#0d6efd',
            showCancelButton: true,
            cancelButtonText: 'Cancelar',
            cancelButtonColor: '#6c757d'
          }).then((result) => {
            if (result.isConfirmed) {
              window.open('/producto/productos', '_blank');
            }
          });
        } else {
          // No hay productos asociados, proceder con descontinuación
          Swal.fire({
            title: '¿Descontinuar pieza?',
            html: `¿Estás seguro que deseas descontinuar la pieza <strong>"${nombrePieza}"</strong>?<br><br>
                   <small class="text-muted">La pieza no estará disponible para nuevos productos pero mantendrá su inventario actual.</small>`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, descontinuar',
            cancelButtonText: 'Cancelar'
          }).then((result) => {
            if (result.isConfirmed) {
              descontinuarPieza(idPieza, nombrePieza);
            }
          });
        }
      } else {
        Swal.fire('Error', data.error, 'error');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      Swal.fire('Error', 'Ocurrió un error al verificar los productos asociados', 'error');
    });
}

// Función para descontinuar pieza
function descontinuarPieza(idPieza, nombrePieza) {
  fetch(`/inventario/descontinuar-pieza/${idPieza}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        Swal.fire({
          title: '¡Pieza descontinuada!',
          text: data.message,
          icon: 'success',
          confirmButtonText: 'Entendido',
          confirmButtonColor: '#0d6efd'
        }).then(() => {
          window.location.reload();
        });
      } else {
        Swal.fire('Error', data.error, 'error');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      Swal.fire('Error', 'Ocurrió un error al descontinuar la pieza', 'error');
    });
}

// Función para reactivar pieza
function reactivarPieza(idPieza, nombrePieza) {
  Swal.fire({
    title: '¿Reactivar pieza?',
    html: `¿Estás seguro que deseas reactivar la pieza <strong>"${nombrePieza}"</strong>?<br><br>
           <small class="text-muted">La pieza volverá a estar disponible para asociar a productos.</small>`,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#28a745',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'Sí, reactivar',
    cancelButtonText: 'Cancelar'
  }).then((result) => {
    if (result.isConfirmed) {
      fetch(`/inventario/reactivar-pieza/${idPieza}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            Swal.fire({
              title: '¡Pieza reactivada!',
              text: data.message,
              icon: 'success',
              confirmButtonText: 'Entendido',
              confirmButtonColor: '#0d6efd'
            }).then(() => {
              window.location.reload();
            });
          } else {
            Swal.fire('Error', data.error, 'error');
          }
        })
        .catch(error => {
          console.error('Error:', error);
          Swal.fire('Error', 'Ocurrió un error al reactivar la pieza', 'error');
        });
    }
  });
}

// Función para eliminación definitiva
function eliminarPiezaDefinitivamente(idPieza, nombrePieza) {
  Swal.fire({
    title: '⚠️ ¡ELIMINACIÓN DEFINITIVA!',
    html: `
      <div class="text-start">
        <p>Estás a punto de <strong>eliminar definitivamente</strong> la pieza:</p>
        <div class="alert alert-danger">
          <strong>${nombrePieza}</strong>
        </div>
        <p><strong>⚠️ ADVERTENCIA:</strong></p>
        <ul class="text-start">
          <li>Esta acción <strong>NO se puede deshacer</strong></li>
          <li>La pieza se eliminará del sistema para siempre</li>
          <li>Solo es posible si no tiene inventario ni historial</li>
        </ul>
        <p>¿Estás <strong>completamente seguro</strong>?</p>
      </div>
    `,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc3545',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'SÍ, ELIMINAR DEFINITIVAMENTE',
    cancelButtonText: 'Cancelar',
    focusCancel: true
  }).then((result) => {
    if (result.isConfirmed) {
      // Segunda confirmación
      Swal.fire({
        title: '¿Estás 100% seguro?',
        text: 'Esta es tu última oportunidad para cancelar',
        icon: 'error',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#28a745',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'No, cancelar'
      }).then((segundaConfirmacion) => {
        if (segundaConfirmacion.isConfirmed) {
          ejecutarEliminacionDefinitiva(idPieza, nombrePieza);
        }
      });
    }
  });
}

function ejecutarEliminacionDefinitiva(idPieza, nombrePieza) {
  fetch(`/inventario/eliminar-pieza-definitivamente/${idPieza}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        Swal.fire({
          title: '¡Eliminada!',
          text: data.message,
          icon: 'success',
          confirmButtonText: 'Entendido',
          confirmButtonColor: '#0d6efd'
        }).then(() => {
          window.location.reload();
        });
      } else {
        Swal.fire('No se puede eliminar', data.error, 'warning');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      Swal.fire('Error', 'Ocurrió un error al eliminar la pieza', 'error');
    });
}

// ========================================
// INICIALIZACIÓN Y EVENT LISTENERS
// ========================================

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    // Actualizar buscador para usar filtros unificados
    document.getElementById('buscadorPiezas').addEventListener('keyup', aplicarFiltros);

    // ========================================
    // FUNCIONALIDAD TRANSFERENCIAS
    // ========================================
    const sucursalOrigenSelect = document.getElementById('id_sucursal_origen_general');
    const sucursalDestinoSelect = document.getElementById('id_sucursal_destino_general');
    const selectorPiezaGeneral = document.getElementById('selectorPiezaGeneral');
    const btnAgregarGeneral = document.getElementById('btnAgregarPiezaGeneral');
    const infoDivGeneral = document.getElementById('infoPiezaSeleccionadaGeneral');

    // Cargar piezas cuando se seleccione sucursal origen
    if (sucursalOrigenSelect) {
        sucursalOrigenSelect.addEventListener('change', function() {
            const sucursalId = this.value;
            if (sucursalId) {
                cargarPiezasPorSucursal(sucursalId);
            } else {
                selectorPiezaGeneral.innerHTML = '<option value="">Primero selecciona la sucursal origen...</option>';
                selectorPiezaGeneral.disabled = true;
                btnAgregarGeneral.disabled = true;
                infoDivGeneral.style.display = 'none';
            }
        });
    }

    // Manejar selección de pieza
    if (selectorPiezaGeneral) {
        selectorPiezaGeneral.addEventListener('change', function () {
            const option = this.options[this.selectedIndex];
            
            if (this.value) {
                const nombrePieza = option.dataset.nombre;
                const disponibles = option.dataset.disponibles;
                
                document.getElementById('nombrePiezaInfoGeneral').textContent = nombrePieza;
                document.getElementById('disponiblesPiezaInfoGeneral').textContent = disponibles;
                infoDivGeneral.style.display = 'block';
                btnAgregarGeneral.disabled = false;
            } else {
                infoDivGeneral.style.display = 'none';
                btnAgregarGeneral.disabled = true;
            }
        });
    }

    // Agregar pieza a la lista
    if (btnAgregarGeneral) {
        btnAgregarGeneral.addEventListener('click', function () {
            const selector = selectorPiezaGeneral;
            const option = selector.options[selector.selectedIndex];

            if (!selector.value) {
                Swal.fire('Error', 'Selecciona una pieza válida', 'error');
                return;
            }

            const idPieza = parseInt(selector.value);
            const nombrePieza = option.dataset.nombre;
            const disponibles = parseInt(option.dataset.disponibles);

            // Verificar si ya está agregada
            const yaExiste = piezasAgregadasGeneral.find(p => p.id === idPieza);
            if (yaExiste) {
                Swal.fire('Error', 'Esta pieza ya está en la lista', 'error');
                return;
            }

            // Agregar pieza
            piezasAgregadasGeneral.push({
                id: idPieza,
                nombre: nombrePieza,
                cantidad: 1,
                disponibles: disponibles
            });

            // Actualizar UI
            actualizarListaPiezasGeneral();
            actualizarResumenTransferenciaGeneral();

            // Limpiar selector
            selector.value = '';
            btnAgregarGeneral.disabled = true;
            infoDivGeneral.style.display = 'none';
        });
    }

    // Limpiar modal cuando se cierre
    const modalTransferencia = document.getElementById('modalTransferenciaGeneral');
    if (modalTransferencia) {
        modalTransferencia.addEventListener('hidden.bs.modal', function () {
            piezasAgregadasGeneral = [];
            sucursalOrigenSelect.value = '';
            sucursalDestinoSelect.value = '';
            selectorPiezaGeneral.innerHTML = '<option value="">Primero selecciona la sucursal origen...</option>';
            selectorPiezaGeneral.disabled = true;
            btnAgregarGeneral.disabled = true;
            infoDivGeneral.style.display = 'none';
            document.getElementById('listaPiezasAgregadasGeneral').style.display = 'none';
            document.getElementById('resumenTransferenciaGeneral').style.display = 'none';
            document.getElementById('btnConfirmarTransferenciaGeneral').disabled = true;
            document.getElementById('observacionesGeneral').value = '';
        });
    }

    // Manejar submit del formulario de transferencia
    const formTransferencia = document.getElementById('formTransferenciaGeneral');
    if (formTransferencia) {
        formTransferencia.addEventListener('submit', function (e) {
            e.preventDefault();

            const sucursalOrigenId = sucursalOrigenSelect.value;
            const sucursalDestinoId = sucursalDestinoSelect.value;
            const observaciones = document.getElementById('observacionesGeneral').value || '';

            if (!sucursalOrigenId || !sucursalDestinoId) {
                Swal.fire('Error', 'Selecciona las sucursales origen y destino', 'error');
                return;
            }

            if (sucursalOrigenId === sucursalDestinoId) {
                Swal.fire('Error', 'La sucursal origen y destino no pueden ser la misma', 'error');
                return;
            }

            if (piezasAgregadasGeneral.length === 0) {
                Swal.fire('Error', 'Agrega al menos una pieza para transferir', 'error');
                return;
            }

            // Preparar datos
            const piezasData = piezasAgregadasGeneral.map(pieza => ({
                id_pieza: parseInt(pieza.id),
                cantidad: parseInt(pieza.cantidad)
            }));

            const transferData = {
                sucursal_origen_id: parseInt(sucursalOrigenId),
                sucursal_destino_id: parseInt(sucursalDestinoId),
                piezas: piezasData,
                observaciones: observaciones
            };

            // Deshabilitar botón
            const btnConfirmar = document.getElementById('btnConfirmarTransferenciaGeneral');
            btnConfirmar.disabled = true;
            btnConfirmar.innerHTML = '<i class="bi bi-hourglass-split"></i> Procesando...';

            // Enviar transferencia
            fetch('/inventario/transferencia-general', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(transferData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: '¡Transferencia Exitosa!',
                        html: `
                            <div style="width: 500px; text-align: left;">
                                <div class="row">
                                    <div class="col-6"><strong>Folio Salida:</strong></div>
                                    <div class="col-6">${data.folio_salida}</div>
                                </div>
                                <div class="row">
                                    <div class="col-6"><strong>Folio Entrada:</strong></div>
                                    <div class="col-6">${data.folio_entrada}</div>
                                </div>
                                <div class="row">
                                    <div class="col-6"><strong>Origen:</strong></div>
                                    <div class="col-6">${data.sucursal_origen}</div>
                                </div>
                                <div class="row">
                                    <div class="col-6"><strong>Destino:</strong></div>
                                    <div class="col-6">${data.sucursal_destino}</div>
                                </div>
                                <div class="row">
                                    <div class="col-6"><strong>Total piezas:</strong></div>
                                    <div class="col-6">${data.total_piezas}</div>
                                </div>
                            </div>
                        `,
                        icon: 'success',
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#0d6efd',
                        allowOutsideClick: false
                    }).then(() => {
                        const modal = bootstrap.Modal.getInstance(document.getElementById('modalTransferenciaGeneral'));
                        modal.hide();
                        window.location.reload();
                    });
                } else {
                    Swal.fire('Error', data.message || 'Error en la transferencia', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire('Error', 'Error en la conexión', 'error');
            })
            .finally(() => {
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = '<i class="bi bi-arrow-left-right"></i> Ejecutar Transferencia';
            });
        });
    }

    // ========================================
    // FUNCIONALIDAD ALTA DE EQUIPOS
    // ========================================
    const selectorPiezaAltaGeneral = document.getElementById('selectorPiezaAltaGeneral');
    const btnAgregarAltaGeneral = document.getElementById('btnAgregarPiezaAltaGeneral');
    const infoDivAltaGeneral = document.getElementById('infoPiezaSeleccionadaAltaGeneral');

    // Event listener para el selector de piezas
    if (selectorPiezaAltaGeneral) {
        selectorPiezaAltaGeneral.addEventListener('change', function () {
            const option = this.options[this.selectedIndex];
            
            if (this.value) {
                const nombrePieza = option.dataset.nombre;
                const categoria = option.dataset.categoria;
                
                document.getElementById('nombrePiezaInfoAltaGeneral').textContent = nombrePieza;
                document.getElementById('categoriaPiezaInfoAltaGeneral').textContent = categoria;
                infoDivAltaGeneral.style.display = 'block';
                btnAgregarAltaGeneral.disabled = false;
            } else {
                infoDivAltaGeneral.style.display = 'none';
                btnAgregarAltaGeneral.disabled = true;
            }
        });
    }

    // Event listener para agregar pieza
    if (btnAgregarAltaGeneral) {
        btnAgregarAltaGeneral.addEventListener('click', function () {
            const selector = selectorPiezaAltaGeneral;
            const option = selector.options[selector.selectedIndex];

            if (!selector.value) {
                Swal.fire('Error', 'Selecciona un tipo de equipo válido', 'error');
                return;
            }

            const idPieza = parseInt(selector.value);
            const nombrePieza = option.dataset.nombre;
            const categoria = option.dataset.categoria;

            // Verificar si ya está agregada
            const yaExiste = piezasAltaEquipoGeneral.find(p => p.id === idPieza);
            if (yaExiste) {
                Swal.fire('Error', 'Este tipo de equipo ya está en la lista', 'error');
                return;
            }

            // Agregar pieza
            piezasAltaEquipoGeneral.push({
                id: idPieza,
                nombre: nombrePieza,
                categoria: categoria,
                cantidad: 1
            });

            // Actualizar UI
            actualizarListaPiezasAltaGeneral();
            actualizarResumenAltaEquipoGeneral();

            // Limpiar selector
            selector.value = '';
            btnAgregarAltaGeneral.disabled = true;
            infoDivAltaGeneral.style.display = 'none';
        });
    }

    // Limpiar modal cuando se cierre
    const modalAltaEquipoGeneral = document.getElementById('modalAltaEquipoGeneral');
    if (modalAltaEquipoGeneral) {
        modalAltaEquipoGeneral.addEventListener('hidden.bs.modal', function () {
            piezasAltaEquipoGeneral = [];
            document.getElementById('id_sucursal_alta_general').value = '';
            if (selectorPiezaAltaGeneral) selectorPiezaAltaGeneral.value = '';
            if (btnAgregarAltaGeneral) btnAgregarAltaGeneral.disabled = true;
            if (infoDivAltaGeneral) infoDivAltaGeneral.style.display = 'none';
            document.getElementById('listaPiezasAgregadasAltaGeneral').style.display = 'none';
            document.getElementById('resumenAltaEquipoGeneral').style.display = 'none';
            document.getElementById('btnConfirmarAltaEquipoGeneral').disabled = true;
            document.getElementById('observacionesAltaGeneral').value = '';
        });
    }

    // Event listener para el formulario de alta
    const formAltaEquipoGeneral = document.getElementById('formAltaEquipoGeneral');
    if (formAltaEquipoGeneral) {
        formAltaEquipoGeneral.addEventListener('submit', function (e) {
            e.preventDefault();

            const sucursalId = document.getElementById('id_sucursal_alta_general').value;
            const observaciones = document.getElementById('observacionesAltaGeneral').value || '';

            if (!sucursalId) {
                Swal.fire('Error', 'Selecciona la sucursal donde registrar los equipos', 'error');
                return;
            }

            if (piezasAltaEquipoGeneral.length === 0) {
                Swal.fire('Error', 'Agrega al menos un tipo de equipo para registrar', 'error');
                return;
            }

            // Preparar datos
            const piezasData = piezasAltaEquipoGeneral.map(pieza => ({
                id_pieza: parseInt(pieza.id),
                cantidad: parseInt(pieza.cantidad)
            }));

            const altaData = {
                sucursal_id: parseInt(sucursalId),
                piezas: piezasData,
                observaciones: observaciones
            };

            // Deshabilitar botón
            const btnConfirmar = document.getElementById('btnConfirmarAltaEquipoGeneral');
            btnConfirmar.disabled = true;
            btnConfirmar.innerHTML = '<i class="bi bi-hourglass-split"></i> Procesando...';

            // Enviar alta
            fetch('/inventario/alta-equipo-general', {
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
                        title: '¡Alta de Equipos Exitosa!',
                        html: `
                            <div style="width: 500px; margin: 0 auto;">
                                <div class="row text-start">
                                    <div class="col-6"><strong>Folio:</strong></div>
                                    <div class="col-6">${data.folio}</div>
                                </div>
                                <div class="row text-start">
                                    <div class="col-6"><strong>Sucursal:</strong></div>
                                    <div class="col-6">${data.sucursal}</div>
                                </div>
                                <div class="row text-start">
                                    <div class="col-6"><strong>Total equipos:</strong></div>
                                    <div class="col-6">${data.total_equipos}</div>
                                </div>
                            </div>
                        `,
                        icon: 'success',
                        confirmButtonText: 'Entendido',
                        allowOutsideClick: false
                    }).then(() => {
                        // Cerrar modal y recargar página
                        modalAltaEquipoGeneral.style.display = 'none';
                        document.querySelector('.modal-backdrop')?.remove();
                        document.body.classList.remove('modal-open');
                        window.location.reload();
                    });
                } else {
                    Swal.fire('Error', data.message || 'Error al procesar el alta', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire('Error', 'Error en la conexión', 'error');
            })
            .finally(() => {
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = '<i class="bi bi-plus-circle"></i> Registrar Equipos';
            });
        });
    }

    // ========================================
    // GESTIÓN DE EQUIPOS (ALTA/BAJA)
    // ========================================
    
    // Event listeners para radio buttons
    document.querySelectorAll('input[name="tipoOperacion"]').forEach(radio => {
        radio.addEventListener('change', cambiarTipoOperacion);
    });
    
    // Event listener para select de equipo en baja
    const tipoEquipoBaja = document.getElementById('tipoEquipoBaja');
    if (tipoEquipoBaja) {
        tipoEquipoBaja.addEventListener('change', actualizarCantidadMaximaBaja);
    }
    
    // Event listener para motivo de baja
    const motivoBaja = document.getElementById('motivoBaja');
    if (motivoBaja) {
        motivoBaja.addEventListener('change', actualizarEstadoBotonConfirmar);
    }
    
    // Event listener para cambio de sucursal
    const sucursalSelect = document.getElementById('id_sucursal_operacion_general');
    if (sucursalSelect) {
        sucursalSelect.addEventListener('change', function() {
            const tipoOperacion = document.querySelector('input[name="tipoOperacion"]:checked')?.value;
            if (tipoOperacion === 'baja') {
                cargarEquiposParaBaja();
            }
        });
    }
    
    // Event listener para modal reset
    const modalGestion = document.getElementById('modalAltaEquipoGeneral');
    if (modalGestion) {
        modalGestion.addEventListener('hidden.bs.modal', function() {
            limpiarFormulariosGestion();
            // Resetear radio buttons
            const radioAlta = document.querySelector('input[name="tipoOperacion"][value="alta"]');
            if (radioAlta) {
                radioAlta.checked = true;
                cambiarTipoOperacion();
            }
        });
        
        // Inicializar modal al abrirse
        modalGestion.addEventListener('show.bs.modal', function() {
            // Asegurar que el radio de alta esté seleccionado por defecto
            const radioAlta = document.querySelector('input[name="tipoOperacion"][value="alta"]');
            if (radioAlta) {
                radioAlta.checked = true;
                cambiarTipoOperacion();
            }
        });
    }
    
    // Event listener para formulario de gestión
    const formGestion = document.getElementById('formAltaEquipoGeneral');
    if (formGestion) {
        formGestion.addEventListener('submit', function(e) {
            e.preventDefault();
            procesarGestionEquipos();
        });
    }
});