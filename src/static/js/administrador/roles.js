// Variable global
let rolAEliminar = null;

// Mostrar modal
function confirmarEliminar(id) {
    rolAEliminar = id;
    const modal = document.getElementById('modalEliminar');
    modal.classList.add('show');
    return false; // evita recargar
}

// Confirmar eliminación
document.getElementById('btnConfirm').addEventListener('click', function() {
    if (rolAEliminar !== null) {
        window.location.href = "/roles/eliminar/" + rolAEliminar;
    }
});

// Cancelar
document.getElementById('btnCancel').addEventListener('click', function() {
    const modal = document.getElementById('modalEliminar');
    modal.classList.remove('show');
    rolAEliminar = null;
});

// Cerrar modal al hacer clic fuera
window.addEventListener('click', function(event) {
    const modal = document.getElementById('modalEliminar');
    if (event.target === modal) {
        modal.classList.remove('show');
        rolAEliminar = null;
    }
});
