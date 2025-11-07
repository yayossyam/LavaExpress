let idUnidadEliminar = null;

function abrirModalEliminar(id) {
    idUnidadEliminar = id;
    const modal = document.getElementById('modalEliminar');
    modal.classList.add('show');
}

function cerrarModalEliminar() {
    const modal = document.getElementById('modalEliminar');
    modal.classList.remove('show');
    idUnidadEliminar = null;
}

document.getElementById('btnConfirmarEliminar').addEventListener('click', function () {
    if (idUnidadEliminar) {
        window.location.href = `/unidadesMedidas/eliminar_unidad/${idUnidadEliminar}`;
    }
});
