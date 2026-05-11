document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // PREMIUM TOAST
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

            icon =
                "bi-exclamation-triangle-fill";

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

    // =========================
    // ELEMENTS
    // =========================

    const variantButtons = document.querySelectorAll(
        ".variant-btn"
    );

    const priceElement = document.getElementById(
        "product-price"
    );

    const stockElement = document.getElementById(
        "stock-status"
    );

    const selectedVariantInput =
        document.getElementById(
            "selected-variant-id"
        );

    const wishlistVariantInput =
        document.getElementById(
            "wishlist-variant-id"
        );

    // =========================
    // IMAGE THUMBNAIL SWITCH
    // =========================

    const thumbnails = document.querySelectorAll(
        ".thumbnail-stack img"
    );

    const mainImg = document.getElementById(
        "main-product-image"
    );

    thumbnails.forEach(thumb => {

        thumb.addEventListener(

            "click",

            function () {

                mainImg.src = this.src;

                thumbnails.forEach(t => {

                    t.classList.remove(
                        "border-active"
                    );
                });

                this.classList.add(
                    "border-active"
                );
            }
        );
    });

    // =========================
    // IMAGE ZOOM EFFECT
    // =========================

    const container = document.querySelector(
        ".main-image-container"
    );

    const image = document.querySelector(
        ".zoom-image"
    );

    if (container && image) {

        container.addEventListener(

            "mousemove",

            (e) => {

                const rect =
                    container.getBoundingClientRect();

                const x =
                    e.clientX - rect.left;

                const y =
                    e.clientY - rect.top;

                const xPercent =
                    (x / rect.width) * 100;

                const yPercent =
                    (y / rect.height) * 100;

                image.style.transformOrigin =
                    `${xPercent}% ${yPercent}%`;

                image.style.transform =
                    "scale(2)";
            }
        );

        container.addEventListener(

            "mouseleave",

            () => {

                image.style.transform =
                    "scale(1)";

                image.style.transformOrigin =
                    "center center";
            }
        );
    }

    // =========================
    // VARIANT CHANGE
    // =========================

    variantButtons.forEach(button => {

        button.addEventListener(

            "click",

            function () {

                // REMOVE ACTIVE

                variantButtons.forEach(btn => {

                    btn.classList.remove(
                        "btn-dark",
                        "active"
                    );

                    btn.classList.add(
                        "btn-outline-dark"
                    );
                });

                // ADD ACTIVE

                this.classList.remove(
                    "btn-outline-dark"
                );

                this.classList.add(
                    "btn-dark",
                    "active"
                );

                // UPDATE PRICE

                const price =
                    this.dataset.price;

                priceElement.innerText =
                    price;

                // UPDATE STOCK

                const stock =
                    parseInt(
                        this.dataset.stock
                    );

                if (stock > 0) {

                    stockElement.innerText =
                        "In Stock";

                    stockElement.classList.remove(
                        "text-danger"
                    );

                    stockElement.classList.add(
                        "text-success"
                    );

                } else {

                    stockElement.innerText =
                        "Out Of Stock";

                    stockElement.classList.remove(
                        "text-success"
                    );

                    stockElement.classList.add(
                        "text-danger"
                    );
                }

                // UPDATE VARIANT IDS

                const variantId =
                    this.dataset.variantId;

                selectedVariantInput.value =
                    variantId;

                wishlistVariantInput.value =
                    variantId;
            }
        );
    });


});