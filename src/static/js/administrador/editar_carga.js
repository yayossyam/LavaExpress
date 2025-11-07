document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.querySelector('#tabla-carga-edit tbody');

    // === ALERTAS ===
    const mensajesActivos = new Set();
    function mostrarAlerta(mensaje, tipo = 'error') {
        if (mensajesActivos.has(mensaje)) return;
        mensajesActivos.add(mensaje);

        const alerta = document.createElement('div');
        alerta.textContent = mensaje;
        alerta.style.backgroundColor = tipo === 'error' ? '#e06666' : '#4BB543';
        alerta.style.color = '#fff';
        alerta.style.padding = '10px 20px';
        alerta.style.borderRadius = '8px';
        alerta.style.marginBottom = '10px';
        alerta.style.position = 'relative';

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
        document.body.appendChild(alerta);

        setTimeout(() => {
            if (alerta.parentNode) {
                alerta.remove();
                mensajesActivos.delete(mensaje);
            }
        }, 5000);
    }

    // === AUTOCOMPLETADO ===
    const sugerenciasBox = document.createElement('div');
    sugerenciasBox.id = 'sugerencias';
    sugerenciasBox.style.position = 'absolute';
    sugerenciasBox.style.zIndex = '1000';
    sugerenciasBox.style.display = 'none';
    document.body.appendChild(sugerenciasBox);

    function mostrarSugerencias(input, materias) {
        const rect = input.getBoundingClientRect();
        sugerenciasBox.style.top = `${rect.bottom + window.scrollY}px`;
        sugerenciasBox.style.left = `${rect.left + window.scrollX}px`;
        sugerenciasBox.style.width = `${rect.width}px`;
        sugerenciasBox.innerHTML = '';

        if (!materias.length) {
            const noRes = document.createElement('div');
            noRes.textContent = 'No se encontraron coincidencias';
            noRes.style.padding = '5px 10px';
            noRes.style.color = '#777';
            sugerenciasBox.appendChild(noRes);
        } else {
            materias.forEach(m => {
                const div = document.createElement('div');
                div.textContent = m.nombre;
                div.dataset.id = m.id;
                div.style.padding = '5px 10px';
                div.style.cursor = 'pointer';
                div.addEventListener('mouseover', () => div.style.backgroundColor = '#f0f0f0');
                div.addEventListener('mouseout', () => div.style.backgroundColor = 'transparent');
                div.addEventListener('click', () => {
                    // cuando el usuario selecciona una sugerencia:
                    input.value = m.nombre;
                    input.dataset.id = m.id;
                    sugerenciasBox.style.display = 'none';
                });
                sugerenciasBox.appendChild(div);
            });
        }
        sugerenciasBox.style.display = 'block';
    }

    document.addEventListener('click', e => {
        if (!sugerenciasBox.contains(e.target) && !e.target.classList.contains('input-nombre')) {
            sugerenciasBox.style.display = 'none';
        }
    });

    // ----------------------------------------------------
    // IMPORTANTE: inicializar dataset.id para inputs ya existentes
    // ----------------------------------------------------
    document.querySelectorAll('#tabla-carga-edit .input-nombre').forEach(inp => {
        // Si el atributo data-id está presente en HTML, convertirlo a dataset (por compatibilidad)
        const attr = inp.getAttribute('data-id');
        if (attr && !inp.dataset.id) inp.dataset.id = attr;
    });

    // === FUNCIONALIDAD DE AGREGAR FILA ===
    function crearFila() {
        const fila = document.createElement('tr');

        // Nombre materia
        const tdNombre = document.createElement('td');
        const inputNombre = document.createElement('input');
        inputNombre.type = 'text';
        inputNombre.placeholder = 'Escribe nombre';
        inputNombre.classList.add('form-control', 'input-nombre');
        inputNombre.dataset.id = '';
        tdNombre.appendChild(inputNombre);

        // Cantidad
        const tdCantidad = document.createElement('td');
        const inputCantidad = document.createElement('input');
        inputCantidad.type = 'number';
        inputCantidad.step = 'any';
        inputCantidad.min = '0';
        inputCantidad.placeholder = '0';
        inputCantidad.classList.add('form-control', 'input-cantidad');
        tdCantidad.appendChild(inputCantidad);

        // Botón eliminar
        const tdEliminar = document.createElement('td');
        const btnEliminar = document.createElement('button');
        btnEliminar.type = 'button';
        btnEliminar.classList.add('btn', 'btn-danger', 'btn-sm');
        btnEliminar.textContent = '➖';
        btnEliminar.addEventListener('click', () => fila.remove());
        tdEliminar.appendChild(btnEliminar);

        fila.appendChild(tdNombre);
        fila.appendChild(tdCantidad);
        fila.appendChild(tdEliminar);

        const ultimaFila = tableBody.querySelector('.ultima-fila');
        tableBody.insertBefore(fila, ultimaFila);
        inputNombre.focus();

        // Autocompletado
        inputNombre.addEventListener('input', async () => {
            inputNombre.dataset.id = '';
            const termino = inputNombre.value.trim();
            if (!termino) {
                sugerenciasBox.style.display = 'none';
                return;
            }
            try {
                const res = await fetch(`/buscar_materia?term=${encodeURIComponent(termino)}`);
                const materias = await res.json();
                mostrarSugerencias(inputNombre, materias);
            } catch (err) {
                mostrarAlerta('Error al autocompletar materias', 'error');
                console.error(err);
            }
        });

        inputNombre.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const primera = sugerenciasBox.querySelector('div:not(.sin-resultados)');
                if (primera) {
                    inputNombre.value = primera.textContent;
                    inputNombre.dataset.id = primera.dataset.id;
                    sugerenciasBox.style.display = 'none';
                }
            }
        });
    }

    // Botón + Agregar Materia Prima
    const ultimaFila = tableBody.querySelector('.ultima-fila');
    if (ultimaFila) {
        const spanAgregar = ultimaFila.querySelector('.agregar-fila');
        spanAgregar.addEventListener('click', crearFila);
    }

    // === VALIDACIÓN ANTES DE SUBMIT ===
    const formEditar = document.getElementById('form-editar-carga');
    formEditar.addEventListener('submit', (e) => {
        const filas = tableBody.querySelectorAll('tr:not(.ultima-fila)');
        if (!filas.length) {
            e.preventDefault();
            mostrarAlerta('Agrega al menos una materia prima', 'error');
            return;
        }

        let valid = true;
        filas.forEach(fila => {
            const inputNombre = fila.querySelector('.input-nombre');
            const inputCantidad = fila.querySelector('.input-cantidad');
            if (!inputNombre.value || !inputCantidad.value || !inputNombre.dataset.id) {
                valid = false;
            }
        });

        if (!valid) {
            e.preventDefault();
            mostrarAlerta('Selecciona una materia prima del autocompletado y asegúrate de que la cantidad sea válida.', 'error');
            return;
        }

        // **ELIMINAR inputs ocultos previos para evitar duplicados**
        formEditar.querySelectorAll('input[type="hidden"]').forEach(i => i.remove());

        // Añadir inputs ocultos con los id correctos (dataset.id)
        filas.forEach(fila => {
            const inputNombre = fila.querySelector('.input-nombre');
            const inputCantidad = fila.querySelector('.input-cantidad');

            const hiddenID = document.createElement('input');
            hiddenID.type = 'hidden';
            hiddenID.name = 'idmateria';
            hiddenID.value = inputNombre.dataset.id;
            formEditar.appendChild(hiddenID);

            const hiddenCantidad = document.createElement('input');
            hiddenCantidad.type = 'hidden';
            hiddenCantidad.name = 'carga';
            hiddenCantidad.value = inputCantidad.value;
            formEditar.appendChild(hiddenCantidad);
        });
    });

    // === ELIMINAR FILAS EXISTENTES ===
    const btnsEliminar = tableBody.querySelectorAll('.eliminar-fila');
    btnsEliminar.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const fila = e.target.closest('tr');
            fila.remove();
        });
    });
});
