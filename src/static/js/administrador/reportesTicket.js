console.log("✅ Reporte de Tickets cargado correctamente");

document.addEventListener("DOMContentLoaded", () => {
    const fechaInicio = document.getElementById("fechaInicio");
    const fechaFinal = document.getElementById("fechaFinal");
    const btnExportar = document.getElementById("btn-exportar-pdf");

    // =====================================================
    // ACORDEÓN NUEVO (ticket-header)
    // =====================================================
    const headers = document.querySelectorAll(".ticket-header");

    headers.forEach(header => {
        const contenido = header.nextElementSibling; // el div .contenido-ticket

        if (!contenido) return;

        // Ocultar al inicio
        contenido.style.display = "none";

        header.addEventListener("click", () => {

            const visible = contenido.style.display === "block";

            // Cerrar todos los demás
            document.querySelectorAll(".contenido-ticket").forEach(c => c.style.display = "none");

            // Abrir/cerrar el actual
            contenido.style.display = visible ? "none" : "block";
        });
    });

    // =====================================================
    // FORMATO DE FECHA A dd/mm/yyyy SOLO VISUAL
    // =====================================================
    document.querySelectorAll(".ticket-date").forEach(span => {
        let fechaISO = span.dataset.date; // yyyy-mm-dd

        if (!fechaISO) return;

        const [y, m, d] = fechaISO.split("-");
        const fechaFormateada = `${d}/${m}/${y}`;

        span.textContent = fechaFormateada;
    });

    // =====================================================
    // VALIDACIONES DE FECHAS (TAL COMO LO TENÍAS)
    // =====================================================
    if (fechaInicio && fechaFinal) {
        const minDate = "2020-01-01";
        fechaInicio.setAttribute("min", minDate);
        fechaFinal.setAttribute("min", minDate);

        fechaInicio.addEventListener("change", () => {
            fechaFinal.min = fechaInicio.value;
        });

        fechaFinal.addEventListener("change", () => {
            if (fechaInicio.value && fechaFinal.value < fechaInicio.value) {
                alert("⚠️ La fecha final no puede ser anterior a la fecha de inicio.");
                fechaFinal.value = "";
            }
        });

        window.addEventListener("pageshow", (event) => {
            const navType = performance.getEntriesByType("navigation")[0]?.type;
            if (event.persisted || navType === "back_forward" || navType === "reload") {
                fechaInicio.value = "";
                fechaFinal.value = "";
            }
        });
    }

    // =====================================================
    // EXPORTAR A PDF (NO MODIFICADO)
    // =====================================================
    if (btnExportar) {
        btnExportar.addEventListener("click", () => {
            let inicio, final;

            if (fechaInicio && fechaFinal) {
                inicio = fechaInicio.value;
                final = fechaFinal.value;
            }

            if (!inicio || !final) {
                inicio = btnExportar.dataset.fechaInicio;
                final = btnExportar.dataset.fechaFinal;
            }

            if (!inicio || !final) {
                alert("⚠️ No se encontraron fechas para exportar el PDF.");
                return;
            }

            console.log(`🧾 Generando PDF de ${inicio} a ${final}...`);

            window.location.href = `/exportar_reporte_tickets?fecha_inicio=${inicio}&fecha_final=${final}`;
        });
    }
});
