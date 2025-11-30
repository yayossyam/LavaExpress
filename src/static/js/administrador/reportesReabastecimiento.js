document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("btn-exportar-pdf");

    if (btn) {
        btn.addEventListener("click", () => {
            const fi = btn.dataset.fechaInicio;
            const ff = btn.dataset.fechaFinal;

            // Ruta CORRECTA y parámetros CORRECTOS
            const url = `/exportar_reabastecimiento_pdf?inicio=${fi}&fin=${ff}`;
            window.location.href = url;
        });
    }
});
