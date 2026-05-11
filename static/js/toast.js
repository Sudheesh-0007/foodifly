// =========================
// GLOBAL PREMIUM TOAST
// =========================

function showToast(

    message,

    type = "success"

) {

    // REMOVE OLD TOAST

    const oldToast =
        document.querySelector(
            ".global-toast"
        );

    if (oldToast) {

        oldToast.remove();
    }

    // ICONS

    let icon = "bi-check-circle-fill";

    let title = "Success";

    if (type === "error") {

        icon = "bi-x-circle-fill";

        title = "Error";
    }

    if (type === "warning") {

        icon = "bi-exclamation-triangle-fill";

        title = "Warning";
    }

    // CREATE TOAST

    const toast =
        document.createElement("div");

    toast.className =
        `global-toast ${type}`;

    toast.innerHTML = `

        <div class="toast-content">

            <div class="toast-icon">

                <i class="bi ${icon}"></i>

            </div>

            <div>

                <h6 class="toast-title">

                    ${title}

                </h6>

                <p class="toast-message">

                    ${message}

                </p>

            </div>

        </div>
    `;

    document.body.appendChild(
        toast
    );

    // SHOW

    setTimeout(() => {

        toast.classList.add(
            "show"
        );

    }, 100);

    // HIDE

    setTimeout(() => {

        toast.classList.remove(
            "show"
        );

        setTimeout(() => {

            toast.remove();

        }, 400);

    }, 3000);
}