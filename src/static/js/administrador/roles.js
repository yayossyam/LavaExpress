// Variable Global para almacenar temporalmente el ID a eliminar
let rolAEliminar = null;

// Función que muestra el modal (ventana emergente). Guarda el ID a eliminar
// Tiene como parametros el ID a eliminar
function confirmarEliminar(id) {
    rolAEliminar = id; //Se guarda el ID a eliminar
    const modal = document.getElementById("confirmModal"); //Obtenemos el modal
    modal.style.display = "flex"; // Mostramos el modal (flex lo centra en pantalla)
    return false; // Evita que el enlace original (<a href="#">) se ejecute y recargue la página
}

// Botón "Sí"
document.getElementById("btnConfirm").addEventListener("click", function() {
    if (rolAEliminar !== null) { //Verifica que haya seleccionado un rol

        //Redigirge a la ruta de eliminacion en app.py
        window.location.href = "/roles/eliminar/" + rolAEliminar; 
    }
});

// Botón "Cancelar"
document.getElementById("btnCancel").addEventListener("click", function() {
    document.getElementById("confirmModal").style.display = "none";
    rolAEliminar = null;
});

// Cerrar modal al dar click fuera de la ventana
window.addEventListener("click", function(event) {
    const modal = document.getElementById("confirmModal");
    if (event.target === modal) {
        modal.style.display = "none"; // Se quita el modal
        rolAEliminar = null; // Limpia la variable
    }
});
