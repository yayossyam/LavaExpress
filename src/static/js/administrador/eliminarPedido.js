// === VARIABLES GLOBALES ===
let pedidoAEliminar = null;

// === MOSTRAR MODAL DE ELIMINACIÓN ===
function confirmarEliminar(idpedido) {
    pedidoAEliminar = idpedido;
    const modalEliminar = document.getElementById("modalEliminar");
    modalEliminar.style.display = "flex";
}

// === CONFIRMAR ELIMINACIÓN ===
document.getElementById("btnEliminarConfirm").addEventListener("click", (e) => {
    e.preventDefault(); // Evita redirección
    if (pedidoAEliminar !== null) {
        fetch(`/pedidos/eliminar_pedido/${pedidoAEliminar}`, { method: 'GET' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Recargar página para reflejar cambios
                    localStorage.setItem("msg_exito", "Pedido eliminado correctamente");
                    window.location.href = "/pedidos"; 
                } else {
                    alert("❌ Error al eliminar el pedido: " + (data.message || ""));
                }
            })
            .catch(err => {
                console.error("Error eliminando pedido:", err);
                alert("❌ Error al eliminar el pedido.");
            });
    }
});

// === CANCELAR ELIMINACIÓN ===
document.getElementById("btnEliminarCancel").addEventListener("click", (e) => {
    e.preventDefault(); // Evita redirección
    const modalEliminar = document.getElementById("modalEliminar");
    modalEliminar.style.display = "none";
    pedidoAEliminar = null;

    // Redirigir a pedidos (opcional si no quieres recargar)
    window.location.href = "/pedidos";
});

// === CERRAR MODAL DE ELIMINACIÓN HACIENDO CLICK FUERA ===
window.addEventListener("click", (event) => {
    const modalEliminar = document.getElementById("modalEliminar");
    if (event.target === modalEliminar) {
        modalEliminar.style.display = "none";
        pedidoAEliminar = null;
        window.location.href = "/pedidos";
    }
});

// === MOSTRAR DETALLES DEL PEDIDO ===
const modalDetalles = document.getElementById("modalDetalles");
const contenidoDetalles = document.getElementById("detallesContenido");

function mostrarDetalles(idpedido) {
    fetch(`/pedidos/detalles/${idpedido}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert(data.message || "Error al obtener detalles");
                return;
            }

            // Limpiar contenido previo
            contenidoDetalles.innerHTML = '';

            // Construir contenido del modal
            const infoHtml = `
                <div class="modal-content">
                    <h3>Detalles Pedido #${data.idpedido}</h3>
                    <div class="pedido-info">
                        <p><strong>Cliente:</strong> ${data.cliente}</p>
                        <p><strong>Fecha de entrega:</strong> ${data.fecha_entrega}</p>
                        <p><strong>Estatus:</strong> ${data.estatus}</p>
                        <p><strong>Servicio:</strong> ${data.servicio}</p>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Prenda</th>
                                <th>Cantidad</th>
                                <th>Peso (kg)</th>
                                <th>Precio x kg</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.prendas.map(p => `
                                <tr>
                                    <td>${p.nombre}</td>
                                    <td>${p.cantidad}</td>
                                    <td>${p.peso}</td>
                                    <td>$${p.precio_x_kg}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    <div class="totales">
                        <p><strong>Peso total:</strong> ${data.peso_total}</p>
                        <p><strong>Costo total:</strong> $${data.costo_total.toFixed(2)}</p>
                    </div>
                    <button type="button" class="btn-cerrar" id="btnCerrarDetalles">Cerrar</button>
                </div>
            `;
            contenidoDetalles.innerHTML = infoHtml;

            // Mostrar modal
            modalDetalles.style.display = "flex";

            // Listener de cierre
            document.getElementById("btnCerrarDetalles").addEventListener("click", () => {
                modalDetalles.style.display = "none";
            });
        })
        .catch(err => {
            console.error("Error cargando detalles:", err);
            alert("Error al cargar los detalles del pedido");
        });
}

// === CERRAR MODAL DETALLES HACIENDO CLICK FUERA ===
window.addEventListener("click", (event) => {
    if (event.target === modalDetalles) {
        modalDetalles.style.display = "none";
    }
});
