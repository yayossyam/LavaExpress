// Variables Globales
let proveedorAEliminar = null;
let proveedorAActualizar = null;

// --- MODAL ELIMINAR ---
function confirmarEliminar(id) {
    proveedorAEliminar = id;
    const modal = document.getElementById("modalEliminar");
    modal.style.display = "flex";
    return false;
}

document.getElementById("btnEliminarConfirm").addEventListener("click", function() {
    if (proveedorAEliminar !== null) {
        window.location.href = "/proveedores/eliminar/" + proveedorAEliminar;
    }
});

document.getElementById("btnEliminarCancel").addEventListener("click", function() {
    document.getElementById("modalEliminar").style.display = "none";
    proveedorAEliminar = null;
});

// --- MODAL ACTUALIZAR ---
function confirmarActualizar(id) {
    proveedorAActualizar = id;
    const modal = document.getElementById("modalActualizar");
    modal.style.display = "flex";
    return false;
}

document.getElementById("btnActualizarConfirm").addEventListener("click", function() {
    if (proveedorAActualizar !== null) {
        document.getElementById("formEditarProveedor").submit();
    }
});

document.getElementById("btnActualizarCancel").addEventListener("click", function() {
    document.getElementById("modalActualizar").style.display = "none";
    proveedorAActualizar = null;
});

// --- Cerrar modales al dar click fuera ---
window.addEventListener("click", function(event) {
    const modalEliminar = document.getElementById("modalEliminar");
    const modalActualizar = document.getElementById("modalActualizar");
    if (event.target === modalEliminar) {
        modalEliminar.style.display = "none";
        proveedorAEliminar = null;
    }
    if (event.target === modalActualizar) {
        modalActualizar.style.display = "none";
        proveedorAActualizar = null;
    }
});
