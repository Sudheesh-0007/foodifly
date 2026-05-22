document.addEventListener("DOMContentLoaded", function () {

    const cancelButtons =
        document.querySelectorAll(".link-item-cancel");

    const confirmBtn =
        document.getElementById("confirmCancelBtn");

    cancelButtons.forEach(button => {

        button.addEventListener("click", function () {

            const url =
                this.getAttribute("data-url");

            // SET CANCEL URL

            confirmBtn.setAttribute("href", url);
        });
    });
});
const orderCancelBtns =
    document.querySelectorAll(".cancel-order-btn");

const confirmOrderCancelBtn =
    document.getElementById("confirmOrderCancelBtn");

orderCancelBtns.forEach(button => {

    button.addEventListener("click", function () {

        const url =
            this.getAttribute("data-url");

        confirmOrderCancelBtn.setAttribute("href", url);
    });
});