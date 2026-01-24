// Script de prueba para verificar cálculos de prefactura
// Ejecutar en la consola del navegador cuando esté abierto el modal de prefactura

console.log('=== Prueba de Cálculos de Prefactura ===');

// Función de redondeo para efectivo
function redondearEfectivo(monto) {
    if (!monto || isNaN(monto)) return 0;
    const entero = Math.floor(monto);
    const centavos = Math.round((monto - entero) * 100);
    if (centavos <= 49) return entero;
    if (centavos >= 60) return entero + 1;
    return entero + 0.5;
}

// Pruebas de redondeo
console.log('Pruebas de redondeo:');
console.log('redondearEfectivo(123.45):', redondearEfectivo(123.45)); // Debe ser 123
console.log('redondearEfectivo(123.49):', redondearEfectivo(123.49)); // Debe ser 123
console.log('redondearEfectivo(123.50):', redondearEfectivo(123.50)); // Debe ser 123.5
console.log('redondearEfectivo(123.60):', redondearEfectivo(123.60)); // Debe ser 124
console.log('redondearEfectivo(123.99):', redondearEfectivo(123.99)); // Debe ser 124

// Verificar elementos del DOM
console.log('Verificación de elementos del DOM:');
console.log('prefactura-subtotal existe:', document.getElementById('prefactura-subtotal') !== null);
console.log('prefactura-iva existe:', document.getElementById('prefactura-iva') !== null);
console.log('pago-total-pago existe:', document.getElementById('pago-total-pago') !== null);

// Verificar valores actuales
const subtotalEl = document.getElementById('prefactura-subtotal');
const ivaEl = document.getElementById('prefactura-iva');
const totalEl = document.getElementById('pago-total-pago');

if (subtotalEl && ivaEl && totalEl) {
    console.log('Valores actuales:');
    console.log('Subtotal:', subtotalEl.textContent);
    console.log('IVA:', ivaEl.textContent);
    console.log('Total:', totalEl.textContent);
    
    // Verificar cálculo
    const subtotal = parseFloat(subtotalEl.textContent) || 0;
    const iva = parseFloat(ivaEl.textContent) || 0;
    const total = parseFloat(totalEl.textContent) || 0;
    const calculado = Math.round((subtotal + iva) * 100) / 100;
    
    console.log('Subtotal + IVA calculado:', calculado);
    console.log('Total mostrado:', total);
    console.log('Cálculo correcto:', calculado === total);
}

// Prueba de precisión decimal
console.log('Pruebas de precisión decimal:');
const test1 = 0.1 + 0.2;
const test1Fixed = Math.round((0.1 + 0.2) * 100) / 100;
console.log('0.1 + 0.2 =', test1, '(problema de precisión)');
console.log('Math.round((0.1 + 0.2) * 100) / 100 =', test1Fixed, '(corregido)');