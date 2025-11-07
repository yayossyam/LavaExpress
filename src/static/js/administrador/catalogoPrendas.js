// ==========================
// VARIABLE GLOBAL PARA ELIMINAR
// ==========================
let prendaAEliminar = null;

// ==========================
// MODAL DE ELIMINAR
// ==========================
function confirmarEliminar(id) {
    prendaAEliminar = id;
    const modal = document.getElementById("modalEliminar");
    modal.style.display = "flex";
}

document.getElementById("btnEliminarConfirm").addEventListener("click", function() {
    if (prendaAEliminar !== null) {
        // Redirigir a la ruta correcta de Flask para eliminar prenda
        window.location.href = "/catalogoPrendas/eliminar_prenda/" + prendaAEliminar;
    }
});

document.getElementById("btnEliminarCancel").addEventListener("click", function() {
    document.getElementById("modalEliminar").style.display = "none";
    prendaAEliminar = null;
});

// Cerrar modal al hacer clic fuera
window.addEventListener("click", function(event) {
    const modalEliminar = document.getElementById("modalEliminar");
    if (event.target === modalEliminar) {
        modalEliminar.style.display = "none";
        prendaAEliminar = null;
    }
});

// ==========================
// ACTUALIZAR PRECIO X KG EN EDITAR
// ==========================
document.addEventListener("DOMContentLoaded", function() {
    const selectCategoria = document.getElementById("categoria");
    const inputPrecio = document.getElementById("precio_categoria");

    if (selectCategoria && inputPrecio) {
        // Obtener todas las categorías y precios del template
        const categorias = Array.from(selectCategoria.options).map(option => ({
            id: option.value,
            precio: option.dataset.precio
        }));

        // Función para actualizar precio
        function actualizarPrecio() {
            const seleccion = selectCategoria.value;
            const cat = categorias.find(c => c.id === seleccion);
            if (cat) {
                inputPrecio.value = `$${cat.precio}`;
            } else {
                inputPrecio.value = "";
            }
        }

        // Inicializa al cargar la página
        actualizarPrecio();

        // Cambiar precio al seleccionar otra categoría
        selectCategoria.addEventListener("change", actualizarPrecio);
    }
});
