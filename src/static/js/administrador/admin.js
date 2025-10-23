let idUsuarioEliminar = null;

function abrirModalEliminar(id) {
    idUsuarioEliminar = id;
    const modal = document.getElementById('modalEliminar');
    modal.classList.add('show');
}

function cerrarModalEliminar() {
    const modal = document.getElementById('modalEliminar');
    modal.classList.remove('show');
    idUsuarioEliminar = null;
}

document.getElementById('btnConfirmarEliminar').addEventListener('click', function () {
    if (idUsuarioEliminar) {
        window.location.href = `/verUsuarios/eliminar_usuarios/${idUsuarioEliminar}`;
    }
});

