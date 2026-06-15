document.addEventListener("DOMContentLoaded", function () {

    const offerType = document.getElementById("offerType");

    const productSection =
        document.getElementById("productSection");

    const categorySection =
        document.getElementById("categorySection");

    function toggleFields() {

        if (offerType.value === "PRODUCT") {

            productSection.style.display = "block";
            categorySection.style.display = "none";

        } else {

            productSection.style.display = "none";
            categorySection.style.display = "block";

        }
    }

    toggleFields();

    offerType.addEventListener(
        "change",
        toggleFields
    );

});