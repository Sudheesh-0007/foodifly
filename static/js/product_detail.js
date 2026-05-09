document.addEventListener('DOMContentLoaded', function() {
    // Handle Weight Button Selection
    const weightBtns = document.querySelectorAll('.weight-btn');
    weightBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            weightBtns.forEach(b => b.classList.remove('active', 'btn-dark'));
            weightBtns.forEach(b => b.classList.add('btn-outline-dark'));
            
            this.classList.add('active', 'btn-dark');
            this.classList.remove('btn-outline-dark');
        });
    });

    // Simple Thumbnail Swapping Logic
    const thumbnails = document.querySelectorAll('.thumbnail-stack img');
    const mainImg = document.querySelector('.main-image-container img');

    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            mainImg.src = this.src;
            thumbnails.forEach(t => t.classList.remove('border-active'));
            this.classList.add('border-active');
        });
    });
});
const container = document.querySelector(
    ".main-image-container"
);

const image = document.querySelector(
    ".zoom-image"
);

container.addEventListener("mousemove", (e) => {

    const rect = container.getBoundingClientRect();

    const x = e.clientX - rect.left;

    const y = e.clientY - rect.top;

    const xPercent = (x / rect.width) * 100;

    const yPercent = (y / rect.height) * 100;

    image.style.transformOrigin =
        `${xPercent}% ${yPercent}%`;

    image.style.transform = "scale(2)";
});

container.addEventListener("mouseleave", () => {

    image.style.transform = "scale(1)";

    image.style.transformOrigin = "center center";
});
// ==============================
// VARIANT PRICE CHANGE
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

        // REMOVE ACTIVE STATE

        variantButtons.forEach(btn => {

            btn.classList.remove(
                "btn-dark",
                "active"
            );

            btn.classList.add(
                "btn-outline-dark"
            );
        });

        // ADD ACTIVE STATE

        this.classList.remove(
            "btn-outline-dark"
        );

        this.classList.add(
            "btn-dark",
            "active"
        );

        // UPDATE PRICE

        const price = this.dataset.price;

        priceElement.innerText = price;

        // UPDATE STOCK

        const stock = this.dataset.stock;

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