document.addEventListener('DOMContentLoaded', () => {
    const tablaPedidos = document.getElementById('tabla-pedidos');
    const detalleBody = document.getElementById('detalle-pedido-body');
    const inputBusqueda = document.getElementById('input-busqueda');

    // Inicializa el modal de Bootstrap
    const modalDetallesEl = document.getElementById('modalDetalles');
    const modalDetalles = new bootstrap.Modal(modalDetallesEl, {
        keyboard: false
    });

    // === Abrir modal con detalles del pedido ===
    tablaPedidos.addEventListener('click', async (e) => {
        if (e.target.classList.contains('btn-detalles')) {
            const idPedido = e.target.dataset.id;

            try {
                const res = await fetch(`/detalle_pedido/${idPedido}`);
                const data = await res.json();

                if (!data.success) {
                    throw new Error(data.message || 'Error al obtener detalles del pedido');
                }

                // Limpia el cuerpo de la tabla
                detalleBody.innerHTML = '';

                // Si no hay prendas
                if (!data.prendas || data.prendas.length === 0) {
                    detalleBody.innerHTML = `<tr><td colspan="4" class="text-center">No hay detalles para este pedido</td></tr>`;
                } else {
                    // Llena la tabla con los datos
                    data.prendas.forEach(item => {
                        detalleBody.innerHTML += `
                            <tr>
                                <td>${item.nombre}</td>
                                <td>${item.cantidad}</td>
                                <td>${item.peso}</td>
                                <td>$${item.precio_x_kg}</td>
                            </tr>
                        `;
                    });

                    // Agrega totales al final
                    detalleBody.innerHTML += `
                        <tr class="fw-bold">
                            <td colspan="2" class="text-end">Peso total:</td>
                            <td>${data.peso_total.toFixed(2)} kg</td>
                            <td></td>
                        </tr>
                        <tr class="fw-bold">
                            <td colspan="3" class="text-end">Costo total:</td>
                            <td>$${data.costo_total.toFixed(2)}</td>
                        </tr>
                    `;
                }

                // Muestra el modal
                modalDetalles.show();

            } catch (error) {
                console.error('❌ Error en fetch:', error);
                alert('No se pudieron cargar los detalles del pedido.');
            }
        }
    });

    // === Filtro de búsqueda ===
    inputBusqueda.addEventListener('keyup', () => {
        const filtro = inputBusqueda.value.trim().toLowerCase();
        const tbody = tablaPedidos.querySelector('tbody');
        let hayCoincidencias = false;

        // Elimina fila de "no coincidencias" si existe
        const filaNoCoinc = document.getElementById('no-coincidencias');
        if (filaNoCoinc) filaNoCoinc.remove();

        tbody.querySelectorAll('tr').forEach(row => {
            if (row.id === 'no-coincidencias') return;

            const id = row.children[0].textContent.trim().toLowerCase();
            const fecha = row.children[1].textContent.trim().toLowerCase();

            const match = (id === filtro) || (fecha.includes(filtro));
            row.style.display = match ? '' : 'none';
            if (match) hayCoincidencias = true;
        });

        // Si no hay coincidencias, mostrar mensaje
        if (!hayCoincidencias && filtro !== '') {
            const tr = document.createElement('tr');
            tr.id = 'no-coincidencias';
            tr.innerHTML = `<td colspan="4" class="text-center">No existen coincidencias</td>`;
            tbody.appendChild(tr);
        }
    });
});
