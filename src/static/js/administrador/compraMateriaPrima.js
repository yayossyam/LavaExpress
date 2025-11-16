document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.querySelector('.table-compra tbody'); 
    const alertContainer = document.getElementById('js-alert-container');

    const mensajesActivos = new Set(); // Evita duplicados
    function mostrarAlerta(mensaje, tipo = 'error') {
        if (mensajesActivos.has(mensaje)) return;
        mensajesActivos.add(mensaje);

        const alerta = document.createElement('div');
        alerta.classList.add('js-alert', `js-alert-${tipo}`);
        alerta.textContent = mensaje;

        if(tipo === 'error') {
            alerta.style.backgroundColor = '#e06666';
            alerta.style.color = '#fff';
            alerta.style.padding = '10px 20px';
            alerta.style.borderRadius = '8px';
            alerta.style.marginBottom = '10px';
            alerta.style.position = 'relative';
        }

        const btnCerrar = document.createElement('span');
        btnCerrar.textContent = '✖';
        btnCerrar.style.position = 'absolute';
        btnCerrar.style.top = '5px';
        btnCerrar.style.right = '10px';
        btnCerrar.style.cursor = 'pointer';
        btnCerrar.addEventListener('click', () => {
            alerta.remove();
            mensajesActivos.delete(mensaje);
        });
        alerta.appendChild(btnCerrar);

        alertContainer.appendChild(alerta);

        setTimeout(() => {
            if (alerta.parentNode) {
                alerta.remove();
                mensajesActivos.delete(mensaje);
            }
        }, 5000);
    }

    // === Autocompletado ===
    const sugerenciasBox = document.createElement('div'); 
    sugerenciasBox.id = 'sugerencias';
    document.body.appendChild(sugerenciasBox); 

    function mostrarSugerencias(input, productos) {
        const rect = input.getBoundingClientRect(); 
        sugerenciasBox.style.display = 'block';
        sugerenciasBox.style.top = `${rect.bottom + window.scrollY}px`;
        sugerenciasBox.style.left = `${rect.left + window.scrollX}px`;
        sugerenciasBox.style.width = `${rect.width}px`;
        sugerenciasBox.innerHTML = '';

        if (productos.length === 0) {
            sugerenciasBox.innerHTML = `<div class="sin-resultados">No se encontraron coincidencias</div>`;
            return;
        }

        productos.forEach(nombreCompleto => {
            const item = document.createElement('div');
            item.textContent = nombreCompleto;

            item.addEventListener('click', () => {
                input.value = nombreCompleto;

                // === CORRECCIÓN ===
                const partes = nombreCompleto.split(' ');

                const cantidadUM = partes[partes.length - 2];   // antepenúltimo
                const unidad = partes[partes.length - 1];       // último
                const nombreBase = partes.slice(0, partes.length - 2).join(' '); // todo lo anterior

                input.dataset.nombreBase = nombreBase;
                input.dataset.cantidadUm = cantidadUM;
                input.dataset.unidad = unidad;
                // === FIN CORRECCIÓN ===

                sugerenciasBox.style.display = 'none';
            });

            sugerenciasBox.appendChild(item);
        });
    }

    document.addEventListener('click', (e) => {
        if (!sugerenciasBox.contains(e.target) && !e.target.classList.contains('input-nombre')) {
            sugerenciasBox.style.display = 'none';
        }
    });

    // === CREAR FILA NUEVA ===
    function crearFila() {
        const fila = document.createElement('tr');

        const tdNombre = document.createElement('td');
        const inputNombre = document.createElement('input');
        inputNombre.type = 'text';
        inputNombre.placeholder = 'Escribe nombre';
        inputNombre.classList.add('input-nombre');
        tdNombre.appendChild(inputNombre);

        const tdCantidad = document.createElement('td');
        const inputCantidad = document.createElement('input');
        inputCantidad.type = 'number';
        inputCantidad.min = '0';
        inputCantidad.placeholder = '0';
        inputCantidad.classList.add('input-cantidad');
        tdCantidad.appendChild(inputCantidad);

        const tdEliminar = document.createElement('td');
        const btnEliminar = document.createElement('button');
        btnEliminar.textContent = '➖';
        btnEliminar.type = 'button';
        btnEliminar.classList.add('btn-delete-row');
        btnEliminar.title = 'Eliminar producto';
        btnEliminar.addEventListener('click', () => fila.remove());
        tdEliminar.appendChild(btnEliminar);

        fila.appendChild(tdNombre);
        fila.appendChild(tdCantidad);
        fila.appendChild(tdEliminar);

        const ultimaFila = tableBody.querySelector('.ultima-fila');
        tableBody.insertBefore(fila, ultimaFila);
        inputNombre.focus();

        inputNombre.addEventListener('input', async () => {
            const termino = inputNombre.value.trim();
            if (termino.length < 1) {
                sugerenciasBox.style.display = 'none';
                return;
            }

            try {
                const res = await fetch(`/buscar_producto?term=${encodeURIComponent(termino)}`);
                const productos = await res.json();
                mostrarSugerencias(inputNombre, productos);
            } catch (err) {
                mostrarAlerta('Error al autocompletar productos', 'error');
                console.error('Error al autocompletar:', err);
            }
        });
    }

    // === Fila botón + ===
    const ultimaFila = document.createElement('tr');
    ultimaFila.classList.add('ultima-fila');
    const tdIcono = document.createElement('td');
    tdIcono.colSpan = 3;
    tdIcono.style.textAlign = 'left';
    tdIcono.innerHTML = '<span class="agregar-fila" style="cursor:pointer; color:#007bff;">+ Agregar Producto</span>';
    ultimaFila.appendChild(tdIcono);
    tableBody.appendChild(ultimaFila);
    tdIcono.addEventListener('click', crearFila);

    // === BOTON GUARDAR ===
    const btnGuardar = document.querySelector('.btn-save');
    btnGuardar.addEventListener('click', () => {
        const idProveedor = document.querySelector('#proveedor').value;
        const fecha = document.querySelector('#fecha').value;

        if (!idProveedor || !fecha) {
            mostrarAlerta('Por favor, complete los campos de Compra General', 'error');
            return;
        }

        const filas = tableBody.querySelectorAll('tr:not(.ultima-fila)');
        const detalle = [];

        filas.forEach(fila => {
            const inputNombre = fila.querySelector('.input-nombre');
            const nombreBase = inputNombre.dataset.nombreBase || inputNombre.value.trim();
            const cantidad = fila.querySelector('.input-cantidad').value.trim();
            const unidad = inputNombre.dataset.unidad || '';
            const cantidadum = inputNombre.dataset.cantidadUm || '';

            if (nombreBase && cantidad && unidad && cantidadum) {
                detalle.push({ nombre: nombreBase, cantidad, unidad, cantidadum });
            }
        });

        if (detalle.length === 0) {
            mostrarAlerta('Agrega al menos un producto con nombre, cantidad y unidad', 'error');
            return;
        }

        const form = document.createElement('form');
        form.method = 'POST';
        form.action = window.location.href;

        const inputProv = document.createElement('input');
        inputProv.type = 'hidden';
        inputProv.name = 'proveedor';
        inputProv.value = idProveedor;
        form.appendChild(inputProv);

        const inputFecha = document.createElement('input');
        inputFecha.type = 'hidden';
        inputFecha.name = 'fecha';
        inputFecha.value = fecha;
        form.appendChild(inputFecha);

        detalle.forEach(item => {
            const inputNombreHidden = document.createElement('input');
            inputNombreHidden.type = 'hidden';
            inputNombreHidden.name = `detalle[][nombre]`;
            inputNombreHidden.value = item.nombre;
            form.appendChild(inputNombreHidden);

            const inputCantidadHidden = document.createElement('input');
            inputCantidadHidden.type = 'hidden';
            inputCantidadHidden.name = `detalle[][cantidad]`;
            inputCantidadHidden.value = item.cantidad;
            form.appendChild(inputCantidadHidden);

            const inputUnidadHidden = document.createElement('input');
            inputUnidadHidden.type = 'hidden';
            inputUnidadHidden.name = `detalle[][unidad]`;
            inputUnidadHidden.value = item.unidad;
            form.appendChild(inputUnidadHidden);

            const inputCantUmHidden = document.createElement('input');
            inputCantUmHidden.type = 'hidden';
            inputCantUmHidden.name = `detalle[][cantidadum]`;
            inputCantUmHidden.value = item.cantidadum;
            form.appendChild(inputCantUmHidden);
        });

        document.body.appendChild(form);
        form.submit();
    });
});
