document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.querySelector('.table-prendas tbody');
    const btnGuardar = document.getElementById('btnGuardar');
    const btnRegresar = document.getElementById('btnRegresar');

    // Crear fila final con botón +
    const ultimaFila = document.createElement('tr');
    ultimaFila.classList.add('ultima-fila-prenda');
    const tdIcono = document.createElement('td');
    tdIcono.colSpan = 4;
    tdIcono.style.textAlign = 'center';
    tdIcono.innerHTML = '<span class="agregar-fila">+ Agregar Prenda</span>';
    ultimaFila.appendChild(tdIcono);
    tableBody.appendChild(ultimaFila);

    // Función para crear una fila de prenda
    function crearFila() {
        const fila = document.createElement('tr');
        fila.classList.add('fila-prenda');

        const tdNombre = document.createElement('td');
        tdNombre.style.position = "relative";
        const inputNombre = document.createElement('input');
        inputNombre.type = 'text';
        inputNombre.placeholder = 'Nombre de prenda';
        inputNombre.classList.add('input-nombre');
        tdNombre.appendChild(inputNombre);

        const tdCantidad = document.createElement('td');
        const inputCantidad = document.createElement('input');
        inputCantidad.type = 'number';
        inputCantidad.min = '0';
        inputCantidad.placeholder = '0';
        tdCantidad.appendChild(inputCantidad);

        const tdPeso = document.createElement('td');
        const inputPeso = document.createElement('input');
        inputPeso.type = 'number';
        inputPeso.min = '0';
        inputPeso.placeholder = '0';
        tdPeso.appendChild(inputPeso);

        const tdEliminar = document.createElement('td');
        const btnEliminar = document.createElement('button');
        btnEliminar.type = 'button';
        btnEliminar.textContent = '➖';
        btnEliminar.classList.add('btn-eliminar-fila');
        btnEliminar.addEventListener('click', () => {
            fila.remove();
            asegurarFilaAgregar();
        });
        tdEliminar.appendChild(btnEliminar);

        const tdId = document.createElement('td'); tdId.style.display = 'none';
        const tdPrecio = document.createElement('td'); tdPrecio.style.display = 'none';

        fila.appendChild(tdNombre);
        fila.appendChild(tdCantidad);
        fila.appendChild(tdPeso);
        fila.appendChild(tdEliminar);
        fila.appendChild(tdId);
        fila.appendChild(tdPrecio);

        tableBody.insertBefore(fila, ultimaFila);
        inputNombre.focus();

        // ===== Autocompletado corregido =====
        inputNombre.addEventListener('input', async () => {
            const termino = inputNombre.value.trim();
            if (!termino) return;

            try {
                const res = await fetch(`/buscar_prenda?term=${encodeURIComponent(termino)}`);
                const prendas = await res.json();

                let lista = tdNombre.querySelector('.sugerencias-list');
                if (!lista) {
                    lista = document.createElement('div');
                    lista.classList.add('sugerencias-list');
                    tdNombre.appendChild(lista);
                }

                lista.innerHTML = '';
                prendas.forEach(p => {
                    const item = document.createElement('div');
                    item.classList.add('sugerencia-item');
                    item.textContent = p.nombre; // ✅ usar la propiedad correcta 'nombre'
                    item.addEventListener('click', () => {
                        inputNombre.value = p.nombre;
                        tdId.textContent = p.id;          // ✅ usar 'id'
                        tdPrecio.textContent = p.precio_kg; // ✅ usar 'precio_kg'
                        lista.innerHTML = '';
                    });
                    lista.appendChild(item);
                });

                if (prendas.length === 0) {
                    const sin = document.createElement('div');
                    sin.classList.add('sin-resultados');
                    sin.textContent = 'No se encontraron coincidencias';
                    lista.appendChild(sin);
                }
            } catch (err) {
                console.error('Error autocompletado:', err);
            }
        });

        inputNombre.addEventListener('keydown', e => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const primera = tdNombre.querySelector('.sugerencia-item');
                if (primera) primera.click();
            }
        });
    }

    function asegurarFilaAgregar() {
        if (!tableBody.querySelector('.ultima-fila-prenda')) {
            tableBody.appendChild(ultimaFila);
        }
    }

    tdIcono.addEventListener('click', crearFila);

    // Cerrar lista de sugerencias al hacer click fuera
    document.addEventListener('click', e => {
        document.querySelectorAll('.sugerencias-list').forEach(lista => {
            if (!lista.contains(e.target) && !e.target.classList.contains('input-nombre')) {
                lista.innerHTML = '';
            }
        });
    });

    // ===== Modal de resumen =====
    const modal = document.getElementById('resumenModal');
    const modalBody = document.getElementById('resumenContenido');

    function mostrarModal(prendas, pesoTotal, costoTotal, idPedido) {
        let html = `<h3>✅ Pedido Registrado</h3>`;
        html += `<p><strong>ID Pedido:</strong> ${idPedido}</p>`;
        html += `<table class="resumen-tabla">
                    <thead>
                        <tr>
                            <th>Prenda</th>
                            <th>Cantidad</th>
                            <th>Peso (kg)</th>
                            <th>Precio/kg</th>
                        </tr>
                    </thead>
                    <tbody>`;
        prendas.forEach(p => {
            html += `<tr>
                        <td>${p.nombre}</td>
                        <td>${p.cantidad}</td>
                        <td>${p.peso}</td>
                        <td>$${p.precio_x_kg}</td>
                    </tr>`;
        });
        html += `</tbody></table>`;
        html += `<div class="resumen-total">Peso Total: <span>${pesoTotal.toFixed(2)} kg</span></div>`;
        html += `<div class="resumen-total">Costo Total: <span>$${costoTotal.toFixed(2)}</span></div>`;
        html += `<button type="button" class="btn-cerrar" id="btnCerrarModalDinamico">Cerrar</button>`;

        modalBody.innerHTML = html;

        document.getElementById('btnCerrarModalDinamico').addEventListener('click', () => {
            modal.classList.remove('show');
        });

        modal.classList.add('show');
    }

    // ===== Guardar Pedido =====
    btnGuardar.addEventListener('click', async () => {
        const cliente = document.getElementById('cliente').value;
        const fecha_entrega = document.getElementById('fecha').value;
        const idservicio = document.getElementById('servicio').value;
        const servicioCostoKg = parseFloat(document.querySelector('#servicio option:checked')?.dataset.costoKg || 0);

        if (!cliente || !fecha_entrega || !idservicio) { alert('Completa todos los campos'); return; }

        const filas = Array.from(document.querySelectorAll('.fila-prenda'));
        if (filas.length === 0) { alert('Agrega al menos una prenda'); return; }

        const prendas = filas.map(fila => ({
            idcatalogo: fila.children[4].textContent,
            nombre: fila.children[0].querySelector('input').value,
            cantidad: parseFloat(fila.children[1].querySelector('input').value),
            peso: parseFloat(fila.children[2].querySelector('input').value),
            precio_x_kg: parseFloat(fila.children[5].textContent)
        }));

        if (prendas.some(p => !p.nombre || !p.cantidad || !p.peso)) { 
            alert('Completa todos los datos de las prendas'); 
            return; 
        }

        let pesoTotal = 0;
        let costoCategorias = 0;
        prendas.forEach(p => {
            pesoTotal += p.peso;
            costoCategorias += p.peso * p.precio_x_kg;
        });
        const costoTotal = costoCategorias + (pesoTotal * servicioCostoKg);

        const data = { iduser: cliente, idservicio, fecha_entrega, prendas, peso_total: pesoTotal, costo_total: costoTotal };

        try {
            const res = await fetch('/nuevoPedido', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await res.json();
            if (result.success) {
                mostrarModal(prendas, pesoTotal, costoTotal, result.idpedido);
                document.getElementById('formPedido').reset();
                tableBody.innerHTML = '';
                tableBody.appendChild(ultimaFila);
            } else {
                alert('❌ Error al registrar el pedido: ' + result.message);
            }
        } catch (err) {
            console.error(err);
            alert('Ocurrió un error al guardar el pedido');
        }
    });

    btnRegresar.addEventListener('click', () => { window.location.href = "/pedidos"; });
});
