// Variables globales
let servicioAEliminar = null;

// Abrir modal
function abrirModalEliminar(id) {
    servicioAEliminar = id;
    const modal = document.getElementById("modalEliminar");
    modal.style.display = "flex"; // Mostramos el modal
}

// Cerrar modal
function cerrarModalEliminar() {
    const modal = document.getElementById("modalEliminar");
    modal.style.display = "none"; // Ocultamos
    servicioAEliminar = null;
}

// Confirmar eliminación
document.getElementById("btnEliminarConfirm").addEventListener("click", function() {
    if (servicioAEliminar !== null) {
        window.location.href = "/servicios/eliminar_servicios/" + servicioAEliminar;
    }
});

// Cancelar eliminación
document.getElementById("btnEliminarCancel").addEventListener("click", function() {
    cerrarModalEliminar();
});

// Cerrar modal al hacer click fuera del contenido
window.addEventListener("click", function(event) {
    const modal = document.getElementById("modalEliminar");
    if (event.target === modal) {
        cerrarModalEliminar();
    }
});
