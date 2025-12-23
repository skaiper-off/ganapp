// Cerrar alertas automáticamente después de 5 segundos
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(400px)';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Confirmar antes de eliminar ganado
function confirmarEliminacion(arete) {
    return confirm(`¿Estás seguro de eliminar el ganado ${arete}?\n\nEsta acción también eliminará todos sus eventos registrados.`);
}

// Validar formulario de registro de ganado
function validarFormularioGanado(form) {
    const arete = form.querySelector('[name="arete"]').value.trim();
    
    if (!arete) {
        alert('⚠️ El número de arete es obligatorio');
        return false;
    }
    
    return true;
}

// Validar formulario de eventos
function validarFormularioEvento(form) {
    const arete = form.querySelector('[name="arete"]').value;
    const tipo = form.querySelector('[name="tipo"]').value;
    
    if (!arete) {
        alert('⚠️ Debes seleccionar un arete');
        return false;
    }
    
    if (!tipo) {
        alert('⚠️ Debes seleccionar un tipo de evento');
        return false;
    }
    
    return true;
}

// Formatear números con separadores de miles
function formatearNumero(numero) {
    return new Intl.NumberFormat('es-MX', {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(numero);
}

// Formatear moneda
function formatearMoneda(cantidad) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(cantidad);
}

// Hacer la fecha de hoy como valor por defecto en inputs de fecha
document.addEventListener('DOMContentLoaded', function() {
    const inputsFecha = document.querySelectorAll('input[type="date"]:not([value])');
    const hoy = new Date().toISOString().split('T')[0];
    
    inputsFecha.forEach(input => {
        if (!input.value) {
            input.value = hoy;
        }
    });
});

// Resaltar fila seleccionada en tablas
document.addEventListener('DOMContentLoaded', function() {
    const filas = document.querySelectorAll('tbody tr');
    
    filas.forEach(fila => {
        fila.addEventListener('click', function() {
            // Remover resaltado de todas las filas
            filas.forEach(f => f.style.outline = 'none');
            // Resaltar fila actual
            this.style.outline = '2px solid var(--secondary)';
        });
    });
});

// Búsqueda en tiempo real
function buscarEnTabla(input, tabla) {
    const filtro = input.value.toLowerCase();
    const filas = tabla.querySelectorAll('tbody tr');
    
    filas.forEach(fila => {
        const texto = fila.textContent.toLowerCase();
        if (texto.includes(filtro)) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
}

// Ordenar tabla por columna
function ordenarTabla(tabla, columna, ascendente = true) {
    const tbody = tabla.querySelector('tbody');
    const filas = Array.from(tbody.querySelectorAll('tr'));
    
    filas.sort((a, b) => {
        const textoA = a.cells[columna].textContent.trim();
        const textoB = b.cells[columna].textContent.trim();
        
        if (ascendente) {
            return textoA.localeCompare(textoB, 'es', { numeric: true });
        } else {
            return textoB.localeCompare(textoA, 'es', { numeric: true });
        }
    });
    
    // Reordenar filas en el DOM
    filas.forEach(fila => tbody.appendChild(fila));
}

// Imprimir página
function imprimirPagina() {
    window.print();
}

// Exportar tabla a CSV (alternativa a Excel)
function exportarTablaCSV(tabla, nombreArchivo) {
    let csv = [];
    const filas = tabla.querySelectorAll('tr');
    
    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('td, th');
        const filaCsv = Array.from(celdas).map(celda => {
            let texto = celda.textContent.trim();
            texto = texto.replace(/"/g, '""'); // Escapar comillas
            return `"${texto}"`;
        }).join(',');
        csv.push(filaCsv);
    });
    
    const csvString = csv.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', nombreArchivo || 'tabla.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

console.log('🐄 GanApp cargado correctamente');