console.log("✅ Reporte de Tickets cargado correctamente");

document.addEventListener("DOMContentLoaded", () => {
    const fechaInicio = document.getElementById("fechaInicio");
    const fechaFinal = document.getElementById("fechaFinal");
    const btnExportar = document.getElementById("btn-exportar-pdf");

    // --- Configurar fechas mínimas y validaciones ---
    if (fechaInicio && fechaFinal) {
        const minDate = "2020-01-01";
        fechaInicio.setAttribute("min", minDate);
        fechaFinal.setAttribute("min", minDate);

        // La fecha final no puede ser anterior a la inicial
        fechaInicio.addEventListener("change", () => {
            fechaFinal.min = fechaInicio.value;
        });

        fechaFinal.addEventListener("change", () => {
            if (fechaInicio.value && fechaFinal.value < fechaInicio.value) {
                alert("⚠️ La fecha final no puede ser anterior a la fecha de inicio.");
                fechaFinal.value = "";
            }
        });

        // Limpiar campos al recargar o volver atrás
        window.addEventListener("pageshow", (event) => {
            const navType = performance.getEntriesByType("navigation")[0]?.type;
            if (event.persisted || navType === "back_forward" || navType === "reload") {
                fechaInicio.value = "";
                fechaFinal.value = "";
            }
        });
    }

    // --- Exportar a PDF ---
    if (btnExportar) {
        btnExportar.addEventListener("click", () => {
            let inicio, final;

            // Intentar obtener fechas de inputs del formulario
            if (fechaInicio && fechaFinal) {
                inicio = fechaInicio.value;
                final = fechaFinal.value;
            }

            // Si no hay fechas en los inputs, usar las del dataset del botón
            if (!inicio || !final) {
                inicio = btnExportar.dataset.fechaInicio;
                final = btnExportar.dataset.fechaFinal;
            }

            if (!inicio || !final) {
                alert("⚠️ No se encontraron fechas para exportar el PDF.");
                return;
            }

            console.log(`🧾 Generando PDF de ${inicio} a ${final}...`);

            // Redirigir a la ruta de Flask para generar PDF
            window.location.href = `/exportar_reporte_tickets?fecha_inicio=${inicio}&fecha_final=${final}`;
        });
    }
});
