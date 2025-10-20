// regresar.js
document.addEventListener('DOMContentLoaded', () => {
    const btnBack = document.querySelector('.btn-back');

    if(btnBack){
        btnBack.addEventListener('click', () => {
            // Opción 1: Regresa a la página anterior en el historial
            window.history.back();

            // Opción 2: Redirigir a una URL específica (descomenta si quieres esto)
            // window.location.href = '/proveedores';
        });
    }
});
