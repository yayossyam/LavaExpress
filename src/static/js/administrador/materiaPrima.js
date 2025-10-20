let idMateriaEliminar = null;

function abrirModalEliminar(id) {
    idMateriaEliminar = id;
    const modal = document.getElementById('modalEliminar');
    modal.classList.add('show');
}

function cerrarModalEliminar() {
    const modal = document.getElementById('modalEliminar');
    modal.classList.remove('show');
    idMateriaEliminar = null;
}

document.getElementById('btnConfirmarEliminar').addEventListener('click', function () {
    if (idMateriaEliminar) {
        window.location.href = `/materiaPrima/eliminar_materia/${idMateriaEliminar}`;
    }
});
