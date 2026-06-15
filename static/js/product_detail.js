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
    const wishlistBtn =
    document.querySelector(
        ".wishlist-btn"
    );

const wishlistIcon =
    wishlistBtn.querySelector("i");    

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
// =========================
// VARIANT CHANGE
// =========================

const addToCartBtn =
    document.querySelector(
        ".add-to-cart-btn"
    );

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


            // =========================
            // UPDATE STOCK
            // =========================

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

                // ENABLE BUTTON

                addToCartBtn.disabled =
                    false;

                addToCartBtn.innerText =
                    "Add To Cart";

                addToCartBtn.classList.remove(
                    "btn-secondary"
                );

                addToCartBtn.classList.add(
                    "btn-dark"
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

                // DISABLE BUTTON

                addToCartBtn.disabled =
                    true;

                addToCartBtn.innerText =
                    "Out Of Stock";

                addToCartBtn.classList.remove(
                    "btn-dark"
                );

                addToCartBtn.classList.add(
                    "btn-secondary"
                );
            }

            // =========================
            // UPDATE VARIANT IDS
            // =========================

            const variantId =
                this.dataset.variantId;
            fetch(`/store/get-variant-price/?variant_id=${variantId}`)

            .then(response => response.json())

            .then(data => {

                if (!data.success) return;

                const offerPrice =
                    document.getElementById("offer-price");

                const originalPrice =
                    document.getElementById("original-price");

                const offerBadge =
                    document.getElementById("offer-badge");

                if (data.has_offer) {

                    offerPrice.innerHTML =
                        `₹${data.offer_price}`;

                    originalPrice.style.display =
                        "inline";

                    originalPrice.innerHTML =
                        `₹${data.price}`;

                    offerBadge.style.display =
                        "inline-block";

                    if (data.discount_type === "PERCENTAGE") {

                        offerBadge.innerHTML =
                            `${data.discount_value}% OFF`;

                    } else {

                        offerBadge.innerHTML =
                            `₹${data.discount_value} OFF`;

                    }

                } else {

                    offerPrice.innerHTML =
                        `₹${data.price}`;

                    originalPrice.style.display =
                        "none";

                    offerBadge.style.display =
                        "none";
                }

            });    

            selectedVariantInput.value =
                variantId;

            wishlistVariantInput.value =
                variantId;
            // =========================
// WISHLIST VISUAL UPDATE
// =========================

const isWishlisted =
    this.dataset.wishlisted;

if (isWishlisted === "true") {

    wishlistBtn.classList.remove(
        "btn-outline-secondary"
    );

    wishlistBtn.classList.add(
        "btn-danger"
    );

    wishlistIcon.classList.remove(
        "bi-heart"
    );

    wishlistIcon.classList.add(
        "bi-heart-fill"
    );

} else {

    wishlistBtn.classList.remove(
        "btn-danger"
    );

    wishlistBtn.classList.add(
        "btn-outline-secondary"
    );

    wishlistIcon.classList.remove(
        "bi-heart-fill"
    );

    wishlistIcon.classList.add(
        "bi-heart"
    );
}    
        }
    );
});


// =========================
// INITIALIZE ACTIVE VARIANT
// =========================

document.addEventListener(

    "DOMContentLoaded",

    function () {

        const activeVariant =
            document.querySelector(
                ".variant-btn.active"
            );

        if (activeVariant) {

            activeVariant.click();
        }
    }
);

});