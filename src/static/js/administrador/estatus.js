// === VARIABLES GLOBALES ===
let idEstatusEliminar = null;

// === ABRIR MODAL DE CONFIRMACIÓN ===
function abrirModalEliminar(id) {
    idEstatusEliminar = id;
    const modal = document.getElementById('modalEliminar');
    modal.classList.add('show');
}

// === CERRAR MODAL ===
function cerrarModalEliminar() {
    const modal = document.getElementById('modalEliminar');
    modal.classList.remove('show');
    idEstatusEliminar = null;
}

// === CONFIRMAR ELIMINACIÓN ===
document.addEventListener('DOMContentLoaded', () => {
    const btnConfirmar = document.getElementById('btnConfirmarEliminar');

    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', () => {
            if (idEstatusEliminar) {
                window.location.href = `/estatus/eliminar_estatus/${idEstatusEliminar}`;
            }
        });
    }
});
