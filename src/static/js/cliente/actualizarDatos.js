// JS para cambiar entre secciones y cerrar sesión
document.addEventListener('DOMContentLoaded', () => {
    const btnPersonales = document.getElementById('btn-personales');
    const btnContrasena = document.getElementById('btn-contrasena');
    const formPersonales = document.getElementById('form-personales');
    const formContrasena = document.getElementById('form-contrasena');

    // --- CAMBIO ENTRE SECCIONES ---
    btnPersonales.addEventListener('click', () => {
        formPersonales.style.display = 'flex';
        formContrasena.style.display = 'none';
        btnPersonales.classList.add('active');
        btnContrasena.classList.remove('active');
    });

    btnContrasena.addEventListener('click', () => {
        formPersonales.style.display = 'none';
        formContrasena.style.display = 'flex';
        btnPersonales.classList.remove('active');
        btnContrasena.classList.add('active');
    });
});
