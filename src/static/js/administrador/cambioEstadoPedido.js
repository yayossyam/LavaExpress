document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("confirmModal");
    const pedidoIdSpan = document.getElementById("m-pedido-id");
    const estadoActualSpan = document.getElementById("m-estado-actual");
    const estadoNuevoSpan = document.getElementById("m-estado-nuevo");
    const btnCancel = document.getElementById("btn-cancel");
    const btnConfirm = document.getElementById("btn-confirm");

    let selectedPedidoId = null;
    let selectedNuevoEstatus = null;

    const abrirModal = (select) => {
        if (!select || select.options.length < 2) return;

        const row = select.closest("tr");
        const btn = row.querySelector(".btn-confirm");
        if (btn.disabled) return;

        selectedPedidoId = select.dataset.pedido;
        selectedNuevoEstatus = select.value;

        pedidoIdSpan.textContent = selectedPedidoId;
        estadoActualSpan.textContent = select.dataset.actual;
        estadoNuevoSpan.textContent = select.options[select.selectedIndex].textContent;

        modal.classList.add("show");
    };

    const tbody = document.querySelector("tbody");

    // Habilitar botón al cambiar select
    tbody.addEventListener("change", (e) => {
        if (e.target.classList.contains("select-estado")) {
            const row = e.target.closest("tr");
            const btn = row.querySelector(".btn-confirm");
            btn.disabled = false;
        }
    });

    // Abrir modal con Enter en select o en el botón Actualizar
    tbody.addEventListener("keydown", (e) => {
        if (e.key !== "Enter") return;

        const row = e.target.closest("tr");
        if (!row) return;

        const select = row.querySelector(".select-estado");
        const btn = row.querySelector(".btn-confirm");

        // Solo si el select existe y el botón no está deshabilitado
        if (select && btn && !btn.disabled) {
            e.preventDefault();
            abrirModal(select);
        }
    });

    // Abrir modal al hacer click en el botón confirmar
    tbody.addEventListener("click", (e) => {
        if (e.target.classList.contains("btn-confirm")) {
            const row = e.target.closest("tr");
            const select = row.querySelector(".select-estado");
            abrirModal(select);
        }
    });

    // Confirmar cambio
    btnConfirm.addEventListener("click", () => {
        if (!selectedPedidoId || !selectedNuevoEstatus) return;

        fetch(window.location.pathname, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id_pedido: selectedPedidoId,
                nuevo_estatus: selectedNuevoEstatus
            })
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) window.location.reload();
            else alert(data.msg || "Error al actualizar");
        })
        .catch(() => alert("Error en la comunicación"));
    });

    // Cancelar modal
    btnCancel.addEventListener("click", () => modal.classList.remove("show"));

    // Escape cierra modal
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") modal.classList.remove("show");
    });
});
