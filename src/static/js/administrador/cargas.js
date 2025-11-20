document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.querySelector('.table-compra tbody'); 
    const alertContainer = document.getElementById('js-alert-container');
    const mensajesActivos = new Set();

    /* === FUNCIONES DE ALERTA === */
    function mostrarAlerta(mensaje, tipo = 'error') {
        if (mensajesActivos.has(mensaje)) return;
        mensajesActivos.add(mensaje);

        const alerta = document.createElement('div');
        alerta.classList.add('js-alert');
        if (tipo === 'success') alerta.classList.add('js-alert-success');

        alerta.innerHTML = `
            <span class="mensaje-alerta">${mensaje}</span>
            <span class="cerrar-alerta">✖</span>
        `;

        alerta.querySelector('.cerrar-alerta').addEventListener('click', () => {
            alerta.remove();
            mensajesActivos.delete(mensaje);
        });

        alertContainer.appendChild(alerta);

        setTimeout(() => {
            if (alerta.parentNode) {
                alerta.remove();
                mensajesActivos.delete(mensaje);
            }
        }, 5000);
    }

    /* === CONFIRMACIÓN ELIMINAR === */
    function mostrarConfirmacion(mensaje, callback) {
        const modal = document.createElement('div');
        modal.classList.add('js-confirm');

        modal.innerHTML = `
            <p>${mensaje}</p>
            <button class="confirm-yes">Sí</button>
            <button class="confirm-no">No</button>
        `;

        document.body.appendChild(modal);

        modal.querySelector('.confirm-yes').addEventListener('click', () => {
            callback(true);
            modal.remove();
        });

        modal.querySelector('.confirm-no').addEventListener('click', () => {
            callback(false);
            modal.remove();
        });
    }

    /* === ELIMINAR FILA / CARGA === */
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const url = e.target.dataset.url;
            mostrarConfirmacion("¿Seguro que deseas eliminar esta carga completa?", (confirmado) => {
                if (confirmado) {
                    window.location.href = url;
                } else {
                    mostrarAlerta("Eliminación cancelada", "success");
                }
            });
        });
    });

    /* === AUTOCOMPLETADO MATERIA PRIMA === */
    const sugerenciasBox = document.createElement('div'); 
    sugerenciasBox.id = 'sugerencias';
    sugerenciasBox.style.display = 'none'; 
    document.body.appendChild(sugerenciasBox); 

    function mostrarSugerencias(input, productos) {
        const rect = input.getBoundingClientRect(); 
        sugerenciasBox.style.top = `${rect.bottom + window.scrollY}px`;
        sugerenciasBox.style.left = `${rect.left + window.scrollX}px`;
        sugerenciasBox.style.width = `${rect.width}px`;
        sugerenciasBox.innerHTML = '';

        if (!productos || productos.length === 0) {
            const noResults = document.createElement('div');
            noResults.textContent = 'No se encontraron coincidencias';
            noResults.classList.add('sin-resultados');
            noResults.style.padding = '5px 10px';
            noResults.style.color = '#777';
            sugerenciasBox.appendChild(noResults);
        } else {
            productos.forEach(materia => { 
                const item = document.createElement('div');
                item.textContent = materia.nombre;
                item.dataset.id = materia.id; 
                item.style.padding = '5px 10px';
                item.style.cursor = 'pointer';
                item.addEventListener('mouseover', () => item.style.backgroundColor = '#f0f0f0');
                item.addEventListener('mouseout', () => item.style.backgroundColor = 'transparent');
                item.addEventListener('click', () => {
                    input.value = materia.nombre;
                    input.dataset.id = materia.id;
                    sugerenciasBox.style.display = 'none';
                });
                sugerenciasBox.appendChild(item);
            });
        }
        sugerenciasBox.style.display = 'block';
    }

    document.addEventListener('click', (e) => {
        if (!sugerenciasBox.contains(e.target) && !e.target.classList.contains('input-nombre')) {
            sugerenciasBox.style.display = 'none';
        }
    });

    /* === CREAR FILA NUEVA === */
    function crearFila() {
        const fila = document.createElement('tr');
        const tdNombre = document.createElement('td');
        const inputNombre = document.createElement('input');
        inputNombre.type = 'text';
        inputNombre.placeholder = 'Escribe nombre de materia prima';
        inputNombre.classList.add('input-nombre');
        inputNombre.dataset.id = '';
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
        btnEliminar.type = 'button';
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
            if (termino.length < 1) {
                sugerenciasBox.style.display = 'none';
                return;
            }
            try {
                const res = await fetch(`/buscar_materia?term=${encodeURIComponent(termino)}`);
                const materias = await res.json();
                mostrarSugerencias(inputNombre, materias);
            } catch (err) {
                mostrarAlerta('Error al autocompletar materias primas', 'error');
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

    const ultimaFila = tableBody.querySelector('.ultima-fila');
    if (ultimaFila) {
        const spanAgregar = ultimaFila.querySelector('.agregar-fila');
        spanAgregar.addEventListener('click', crearFila);
    }

    /* === VALIDACIÓN FORMULARIO ANTES DE ENVIAR === */
    const formCargas = document.getElementById('form-nueva-carga');
    formCargas.addEventListener('submit', (e) => {
        const idCategoria = document.querySelector('#categoria').value;
        if (!idCategoria) {
            e.preventDefault();
            mostrarAlerta('Selecciona una categoría', 'error');
            return;
        }

        const filas = tableBody.querySelectorAll('tr:not(.ultima-fila)');
        if (filas.length === 0) {
            e.preventDefault();
            mostrarAlerta('Agrega al menos una materia prima', 'error');
            return;
        }

        let valid = true;
        filas.forEach(fila => {
            const inputNombre = fila.querySelector('.input-nombre');
            const cantidad = fila.querySelector('.input-cantidad').value.trim();
            const idMateria = inputNombre.dataset.id;
            if (!inputNombre.value || !cantidad || !idMateria || isNaN(parseInt(idMateria))) {
                valid = false;
            }
        });

        if (!valid) {
            e.preventDefault();
            mostrarAlerta('Selecciona Materia Prima del autocompletado y cantidad válida.', 'error');
            return;
        }

        // Agregar inputs hidden para enviar ids y cantidades
        filas.forEach(fila => {
            const inputNombre = fila.querySelector('.input-nombre');
            const cantidad = fila.querySelector('.input-cantidad').value.trim();
            const idMateria = inputNombre.dataset.id;

            const hiddenID = document.createElement('input');
            hiddenID.type = 'hidden';
            hiddenID.name = 'idmateria';
            hiddenID.value = idMateria;
            formCargas.appendChild(hiddenID);

            const hiddenCantidad = document.createElement('input');
            hiddenCantidad.type = 'hidden';
            hiddenCantidad.name = 'carga';
            hiddenCantidad.value = cantidad;
            formCargas.appendChild(hiddenCantidad);
        });
    });
});
