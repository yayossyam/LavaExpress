document.addEventListener('DOMContentLoaded', () => {
    const selectsEstado = document.querySelectorAll('.select-estado');
    const modalConfirm = document.getElementById('confirmModal');
    const modalFaltantes = document.getElementById('faltantesModal');
    const btnConfirm = document.getElementById('btn-confirm');
    const btnCancel = document.getElementById('btn-cancel');
    const faltantesBody = document.getElementById('faltantes-body');
    const btnCerrarFaltantes = document.getElementById('btn-cerrar-faltantes');

    const pedidoIdSpan = document.getElementById('m-pedido-id');
    const estadoActualSpan = document.getElementById('m-estado-actual');
    const estadoNuevoSpan = document.getElementById('m-estado-nuevo');

    let pedidoSeleccionado = null;
    let nuevoEstatus = null;

    // === ALERTAS TIPO TOAST ===
    const alertContainer = document.createElement('div');
    alertContainer.style.position = 'fixed';
    alertContainer.style.top = '20px';
    alertContainer.style.right = '20px';
    alertContainer.style.zIndex = '9999';
    document.body.appendChild(alertContainer);

    function mostrarAlerta(mensaje, tipo = 'success') {
        const alerta = document.createElement('div');
        alerta.textContent = mensaje;
        alerta.style.padding = '12px 18px';
        alerta.style.marginBottom = '10px';
        alerta.style.borderRadius = '10px';
        alerta.style.fontWeight = '600';
        alerta.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
        alerta.style.transition = 'opacity 0.3s';
        alerta.style.whiteSpace = 'pre-line'; // permite saltos de línea

        alerta.style.backgroundColor = tipo === 'success' ? '#28a745' : '#e06666';
        alerta.style.color = 'white';

        alertContainer.appendChild(alerta);
        setTimeout(() => {
            alerta.style.opacity = '0';
            setTimeout(() => alerta.remove(), 300);
        }, 5000);
    }

    // === MODALES ===
    function abrirModal(modal) {
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        document.body.style.overflow = 'hidden';
    }

    function cerrarModal(modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }

    btnCancel?.addEventListener('click', () => cerrarModal(modalConfirm));
    btnCerrarFaltantes?.addEventListener('click', () => cerrarModal(modalFaltantes));

    // === CAMBIO DE ESTADO ===
    selectsEstado.forEach(select => {
        const btn = select.closest('tr').querySelector('.btn-confirm');
        const estatusActual = select.dataset.actual;
        const idPedido = select.dataset.pedido;

        select.addEventListener('change', () => {
            btn.disabled = false;
            btn.addEventListener('click', () => {
                pedidoSeleccionado = parseInt(idPedido);
                nuevoEstatus = parseInt(select.value);

                pedidoIdSpan.textContent = idPedido;
                estadoActualSpan.textContent = estatusActual;
                estadoNuevoSpan.textContent = select.options[select.selectedIndex].text;

                abrirModal(modalConfirm);
            }, { once: true });
        });
    });

    // === CONFIRMAR CAMBIO ===
    btnConfirm.addEventListener('click', async () => {
        if (!pedidoSeleccionado || !nuevoEstatus) return;

        btnConfirm.disabled = true;
        btnConfirm.textContent = "Procesando...";

        try {
            const response = await fetch('/cambioEstadoPedido', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id_pedido: pedidoSeleccionado,
                    nuevo_estatus: nuevoEstatus
                })
            });

            const result = await response.json();
            console.log("Respuesta del servidor:", result);

            if (response.ok && result.success) {
                mostrarAlerta('Estado actualizado correctamente ✅', 'success');
                cerrarModal(modalConfirm);
                setTimeout(() => window.location.reload(), 1500);
            } else {
                cerrarModal(modalConfirm);
                if (result.msg && result.msg.includes("materia prima")) {
                    // Si el mensaje contiene faltantes, mostrar modal con detalle
                    faltantesBody.textContent = result.msg;
                    abrirModal(modalFaltantes);
                } else {
                    mostrarAlerta(result.msg || 'Error al actualizar el estado ❌', 'error');
                }
            }

        } catch (err) {
            console.error('Error:', err);
            mostrarAlerta('Error de conexión con el servidor ⚠️', 'error');
            cerrarModal(modalConfirm);
        } finally {
            btnConfirm.disabled = false;
            btnConfirm.textContent = "Confirmar";
        }
    });

    // === CERRAR MODALES AL CLIC FUERA ===
    window.addEventListener('click', (e) => {
        if (e.target === modalConfirm) cerrarModal(modalConfirm);
        if (e.target === modalFaltantes) cerrarModal(modalFaltantes);
    });

    // === BUSCADOR DE PEDIDOS ===
    const inputBuscar = document.getElementById('id_pedido');
    if (inputBuscar) {
        inputBuscar.addEventListener('input', () => {
            clearTimeout(window._buscarTimer);
            window._buscarTimer = setTimeout(() => {
                const valor = inputBuscar.value.trim();
                const url = new URL(window.location.href);
                if (valor) url.searchParams.set('id_pedido', valor);
                else url.searchParams.delete('id_pedido');
                window.location.href = url.toString();
            }, 800);
        });
    }
});
