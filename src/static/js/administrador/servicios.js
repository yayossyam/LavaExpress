//Creamos variable global
let idServicioEliminar = null;

//Abrir modal para confirmar eliminación
function abrirModalEliminar(id) {
    idServicioEliminar = id;
    const modal = document.getElementById('modalEliminar')
    modal.classList.add('show');
}

//Cerrar modal para confirmar eliminaciín
function cerrarModalEliminar() {
    const modal = document.getElementById('modalEliminar');
    modal.classList.remove('show');
    idServicioEliminar = null;
}

//Confirmación de eliminación
document.getElementById('btnConfirmarEliminar').addEventListener('click', function() {
    if (idServicioEliminar) {
        window.location.href = `/servicios/eliminar_servicios/${idServicioEliminar}`;
    }
});