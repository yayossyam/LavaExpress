document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-editar-pedido');
    const tablaPrendas = document.querySelector('#tabla-editar-prendas tbody');
    const pedidoId = form.dataset.id;

    // ===== Crear nueva fila =====
    function crearFila() {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td class="input-nombre-sugerencia">
                <input type="text" class="form-control input-nombre" placeholder="Prenda">
                <div class="sugerencias-list"></div>
            </td>
            <td><input type="number" class="form-control input-cantidad" value="1" min="1"></td>
            <td><input type="number" class="form-control input-peso" value="0" step="any" min="0"></td>
            <td><button type="button" class="btn btn-danger btn-sm eliminar-fila">➖</button></td>
        `;
        tablaPrendas.insertBefore(fila, tablaPrendas.querySelector('.ultima-fila'));
        agregarEventosFila(fila, false);
    }

    // ===== Eventos por fila =====
    function agregarEventosFila(fila, readonly=false) {
        const btnEliminar = fila.querySelector('.eliminar-fila');
        if(btnEliminar) btnEliminar.addEventListener('click', () => { fila.remove(); calcularTotales(); });

        const inputNombre = fila.querySelector('.input-nombre');
        const contSugerencias = fila.querySelector('.sugerencias-list');

        if(!readonly) {
            inputNombre.addEventListener('input', async () => {
                const termino = inputNombre.value.trim();
                contSugerencias.innerHTML = '';
                if(!termino){ 
                    contSugerencias.style.display='none'; 
                    return; 
                }

                try {
                    const res = await fetch(`/buscar_prenda?term=${encodeURIComponent(termino)}`);
                    const prendas = await res.json();

                    if(!prendas.length){
                        contSugerencias.innerHTML = '<div class="no-coincidencias">No se encontraron coincidencias</div>';
                        contSugerencias.style.display = 'block';
                        return;
                    }

                    prendas.forEach(p => {
                        const div = document.createElement('div');
                        div.textContent = p.nombre;
                        div.dataset.id = p.id;
                        div.dataset.precio = p.precio_kg;
                        div.addEventListener('click', () => {
                            inputNombre.value = p.nombre;
                            inputNombre.dataset.id = p.id;
                            inputNombre.dataset.precio = p.precio_kg;
                            contSugerencias.style.display='none';
                            calcularTotales();
                        });
                        contSugerencias.appendChild(div);
                    });
                    contSugerencias.style.display='block';
                } catch(err){ console.error(err); }
            });
        }

        document.addEventListener('click', e => {
            if(!fila.contains(e.target)) contSugerencias.style.display='none';
        });

        fila.querySelectorAll('.input-peso, .input-cantidad').forEach(input => input.addEventListener('input', calcularTotales));
    }

    // Inicializar filas existentes
    tablaPrendas.querySelectorAll('tr:not(.ultima-fila)').forEach(f => agregarEventosFila(f, true));
    tablaPrendas.querySelector('.agregar-fila').addEventListener('click', crearFila);

    // ===== Calcular totales =====
    function calcularTotales() {
        let pesoTotal = 0;
        let total = 0;

        const servicioSelect = document.getElementById('servicio');
        const costoKgServicio = parseFloat(servicioSelect.selectedOptions[0].dataset.costoKg || 0);

        tablaPrendas.querySelectorAll('tr:not(.ultima-fila)').forEach(fila => {
            const cantidad = parseFloat(fila.querySelector('.input-cantidad').value) || 0;
            const peso = parseFloat(fila.querySelector('.input-peso').value) || 0;
            pesoTotal += peso;
            const precioKg = parseFloat(fila.querySelector('.input-nombre').dataset.precio || 0);
            total += peso * precioKg;
        });

        // Total final considerando costo del servicio
        total += pesoTotal * costoKgServicio;

        // Mostrar en inputs ocultos si los tienes
        const totalInput = document.getElementById('total');
        if(totalInput) totalInput.value = total.toFixed(2);

        const pesoInput = document.getElementById('pesototal');
        if(pesoInput) pesoInput.value = pesoTotal.toFixed(2);
    }

    // ===== Cuando cambia el servicio =====
    document.getElementById('servicio').addEventListener('change', calcularTotales);

    // ===== Enviar formulario =====
    form.addEventListener('submit', async e => {
        e.preventDefault();

        // Construir array de prendas
        const prendas = [];
        tablaPrendas.querySelectorAll('tr:not(.ultima-fila)').forEach(fila => {
            const nombreInput = fila.querySelector('.input-nombre');
            if(!nombreInput.dataset.id) return; // ignorar si no seleccionó prenda
            const cantidad = parseFloat(fila.querySelector('.input-cantidad').value) || 0;
            const peso = parseFloat(fila.querySelector('.input-peso').value) || 0;

            prendas.push({
                idcatalogo: nombreInput.dataset.id,  // coincide con app.py
                cantidad,
                peso
            });
        });

        const payload = {
            iduser: document.getElementById('cliente').value,
            idservicio: document.getElementById('servicio').value,
            fecha_entrega: document.getElementById('fecha_entrega').value,
            prendas
        };

        try {
            const res = await fetch(`/pedidos/editar/${pedidoId}`, {  // ruta corregida
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if(data.success){
                Swal.fire('¡Éxito!', 'Pedido actualizado correctamente', 'success')
                    .then(() => { window.location.href = '/pedidos'; });
            } else {
                Swal.fire('Error', data.message || 'Algo salió mal', 'error');
            }
        } catch(err){
            console.error(err);
            Swal.fire('Error', 'No se pudo conectar con el servidor', 'error');
        }
    });

    // ===== Calcular totales iniciales =====
    calcularTotales();
});
