console.log("✅ Reporte de Ventas cargado correctamente");

document.addEventListener("DOMContentLoaded", () => {
    const fechaInicio = document.getElementById("fechaInicio");
    const fechaFinal = document.getElementById("fechaFinal");

    // --- Configurar fechas mínimas y validaciones ---
    if (fechaInicio && fechaFinal) {
        const minDate = "2020-01-01";
        fechaInicio.setAttribute("min", minDate);
        fechaFinal.setAttribute("min", minDate);

        // Cuando se selecciona la fecha de inicio, la final no puede ser anterior
        fechaInicio.addEventListener("change", () => {
            fechaFinal.min = fechaInicio.value;
        });

        fechaFinal.addEventListener("change", () => {
            if (fechaInicio.value && fechaFinal.value < fechaInicio.value) {
                alert("⚠️ La fecha final no puede ser anterior a la fecha de inicio.");
                fechaFinal.value = "";
            }
        });

        // --- Limpiar campos al recargar o volver atrás ---
        window.addEventListener("pageshow", (event) => {
            const navType = performance.getEntriesByType("navigation")[0]?.type;
            // Si la página viene del historial o se recarga, limpiar los valores
            if (event.persisted || navType === "back_forward" || navType === "reload") {
                fechaInicio.value = "";
                fechaFinal.value = "";
            }
        });
    }

    // --- Confirmación visual al exportar PDF ---
    const btnExportar = document.getElementById("btnExportarPDF");
    if (btnExportar) {
        btnExportar.addEventListener("click", () => {
            console.log("🧾 Generando reporte PDF...");
        });
    }
});
