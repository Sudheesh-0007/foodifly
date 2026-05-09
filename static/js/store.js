function changeImage(element) {

    document.getElementById(
        "main-image"
    ).src = element.src;

    document.querySelectorAll(
        ".thumb-image"
    ).forEach(img => {

        img.classList.remove(
            "border-active"
        );
    });

    element.classList.add(
        "border-active"
    );
}

// ==============================
// VARIANT SELECTION
// ==============================

const variantButtons = document.querySelectorAll(
    ".variant-btn"
);

const priceElement = document.getElementById(
    "product-price"
);

const stockElement = document.getElementById(
    "stock-status"
);

variantButtons.forEach(button => {

    button.addEventListener("click", function () {

        variantButtons.forEach(btn => {

            btn.classList.remove(
                "btn-dark"
            );

            btn.classList.add(
                "btn-outline-dark"
            );
        });

        this.classList.remove(
            "btn-outline-dark"
        );

        this.classList.add(
            "btn-dark"
        );

        const price = this.dataset.price;

        const stock = this.dataset.stock;

        priceElement.innerText = price;

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
    });
});