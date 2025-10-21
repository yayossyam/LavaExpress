/** Creamos una variable global */
let idMateriaEliminar = null;

/** Creamos función para mostrar el modal de eliminar */
function abrirModalEliminar(id) {
    idMateriaEliminar = id;
    const modal = document.getElementById('modalEliminar');
    modal.classList.add('show');
}

/** Creamos función para cerrar el modal de eliminar */
function cerrarModalEliminar() {
    const modal = document.getElementById('modalEliminar');
    modal.classList.remove('show'); /** Quita el modal */
    idMateriaEliminar = null; /** Limpia el valor de la variable global */
}

/** Función para confirmar eliminar el dato */
document.getElementById('btnConfirmarEliminar').addEventListener('click', function() {
    if(idMateriaEliminar) {
        window.location.href = `/categoriaPrenda/eliminar_categoria/${idMateriaEliminar}`;
    }
});

