document.addEventListener('DOMContentLoaded', () => {

    // === ELIMINAR PEDIDO ===
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', async () => {
            const idPedido = btn.dataset.id;
            if (!confirm(`¿Deseas eliminar el pedido #${idPedido}?`)) return;

            try {
                const res = await fetch(`/eliminarPedido/${idPedido}`, {
                    method: 'DELETE'
                });
                const data = await res.json();
                if (data.success) {
                    alert(`Pedido #${idPedido} eliminado correctamente`);
                    // Quitar fila de la tabla
                    btn.closest('tr').remove();
                } else {
                    alert(`Error al eliminar: ${data.message}`);
                }
            } catch (err) {
                console.error(err);
                alert('Ocurrió un error al eliminar el pedido');
            }
        });
    });

    // === MODAL DETALLES ===
    document.querySelectorAll('.btn-detalles').forEach(btn => {
        btn.addEventListener('click', () => {
            const prendas = JSON.parse(btn.dataset.prendas);
            const servicio = btn.dataset.servicio;
            const pedidoId = btn.dataset.id;

            // Agrupar por categoría y ordenar
            const categorias = {};
            prendas.forEach(p => {
                if (!categorias[p.CATEGORIA]) categorias[p.CATEGORIA] = [];
                categorias[p.CATEGORIA].push(p);
            });

            let html = `<h5>Pedido ID: ${pedidoId}</h5>`;
            html += `<p>Tipo de Servicio: <strong>${servicio}</strong></p>`;
            html += `<table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Prenda</th>
                                <th>Categoría</th>
                                <th>Cantidad</th>
                                <th>Peso (kg)</th>
                            </tr>
                        </thead>
                        <tbody>`;
            for (const cat of Object.keys(categorias).sort()) {
                categorias[cat].forEach(p => {
                    html += `<tr>
                                <td>${p.NOMBREPRENDA}</td>
                                <td>${cat}</td>
                                <td>${p.CANTIDAD}</td>
                                <td>${p.PESO}</td>
                            </tr>`;
                });
            }
            html += `</tbody></table>`;

            document.getElementById('modalDetallesBody').innerHTML = html;
            new bootstrap.Modal(document.getElementById('modalDetalles')).show();
        });
    });

});
