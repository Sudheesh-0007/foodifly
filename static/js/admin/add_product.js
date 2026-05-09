const productName = document.getElementById("id_product_name");
const slugField = document.getElementById("id_slug");

productName.addEventListener("keyup", function () {

    let slug = productName.value
        .toLowerCase()
        .trim()
        .replace(/[^\w\s-]/g, "")
        .replace(/\s+/g, "-");

    slugField.value = slug;
});


const imageInput = document.getElementById("image-input");

const previewContainer = document.getElementById(
    "image-preview-container"
);

const form = document.getElementById("addProductForm");

const imageToCrop = document.getElementById("image-to-crop");

const cropBtn = document.getElementById("crop-btn");

const cancelCropBtn = document.getElementById(
    "cancel-crop-btn"
);

const cropperModal = new bootstrap.Modal(
    document.getElementById("cropperModal")
);

let cropper;

let selectedFiles = [];

let fileQueue = [];

let currentFileIndex = 0;


// ==============================
// IMAGE SELECT
// ==============================

imageInput.addEventListener("change", function (e) {

    const files = Array.from(e.target.files);

    fileQueue = files;

    currentFileIndex = 0;

    openCropper(fileQueue[currentFileIndex]);

    imageInput.value = "";
});


// ==============================
// OPEN CROPPER
// ==============================

function openCropper(file) {

    const reader = new FileReader();

    reader.onload = function (event) {

        imageToCrop.src = event.target.result;

        cropperModal.show();

        imageToCrop.onload = () => {

            if (cropper) {
                cropper.destroy();
            }

            cropper = new Cropper(imageToCrop, {

                aspectRatio: 1,

                viewMode: 1,

                autoCropArea: 1,

                responsive: true,
            });
        };
    };

    reader.readAsDataURL(file);
}


// ==============================
// CROP IMAGE
// ==============================

cropBtn.addEventListener("click", function () {

    const canvas = cropper.getCroppedCanvas({

        width: 800,

        height: 800,
    });

    canvas.toBlob((blob) => {

        const file = new File(

            [blob],

            `cropped_${Date.now()}.jpg`,

            {
                type: "image/jpeg",
            }
        );

        selectedFiles.push(file);

        renderPreviews();

        cropper.destroy();

        currentFileIndex++;

        // Next image
        if (currentFileIndex < fileQueue.length) {

            openCropper(fileQueue[currentFileIndex]);

        } else {

            cropperModal.hide();
        }

    }, "image/jpeg", 0.9);
});


// ==============================
// RENDER PREVIEWS
// ==============================

function renderPreviews() {

    // REMOVE ONLY NEW IMAGE PREVIEWS

    const newPreviews = document.querySelectorAll(
        ".new-image-preview"
    );

    newPreviews.forEach(preview => {

        preview.remove();
    });

    // RENDER NEWLY ADDED IMAGES

    selectedFiles.forEach((file, index) => {

        const reader = new FileReader();

        reader.onload = function (event) {

            const wrapper =
                document.createElement("div");

            wrapper.className =
                "preview-image-wrapper new-image-preview";

            const img =
                document.createElement("img");

            img.src = event.target.result;

            img.className =
                "preview-thumbnail";

            const removeBtn =
                document.createElement("button");

            removeBtn.innerHTML = "×";

            removeBtn.className =
                "remove-image-btn";

            removeBtn.type = "button";

            removeBtn.addEventListener(
                "click",
                () => {

                    selectedFiles.splice(
                        index,
                        1
                    );

                    renderPreviews();
                }
            );

            wrapper.appendChild(img);

            wrapper.appendChild(removeBtn);

            previewContainer.appendChild(
                wrapper
            );
        };

        reader.readAsDataURL(file);
    });
}


// ==============================
// CANCEL CROPPING
// ==============================

cancelCropBtn.addEventListener("click", function () {

    cropper.destroy();

    cropperModal.hide();

    fileQueue = [];

    currentFileIndex = 0;
});


// ==============================
// FORM SUBMIT
// ==============================

form.addEventListener("submit", function (e) {

    // Existing images already displayed
    const existingImages = document.querySelectorAll(
        "#image-preview-container .preview-image-wrapper"
    ).length;

    // Newly uploaded images
    const newImages = selectedFiles.length;

    // Total images
    const totalImages = existingImages + newImages;

    console.log("Existing:", existingImages);
    console.log("New:", newImages);
    console.log("Total:", totalImages);

    if (totalImages < 3) {

        e.preventDefault();

        alert("Minimum 3 images required");

        return;
    }

    // Only attach new uploaded files
    if (selectedFiles.length > 0) {

        const dataTransfer = new DataTransfer();

        selectedFiles.forEach(file => {

            dataTransfer.items.add(file);
        });

        imageInput.files = dataTransfer.files;
    }
});

const addVariantBtn = document.getElementById("add-variant-btn");

const variantsContainer = document.getElementById("variants-container");


// =======================
// ADD VARIANT
// =======================

addVariantBtn.addEventListener("click", function () {

    const variantRow = document.createElement("div");

    variantRow.className =
        "d-flex align-items-end gap-3 variant-row mb-3";

variantRow.innerHTML = `

    <!-- VARIANT -->
    <div class="flex-fill">

        <label class="custom-label d-block">
            Variant
        </label>

        <input
            type="text"
            name="variant_values[]"
            class="form-control custom-input"
            placeholder="500ml, 1kg"
            required
        >

    </div>

    <!-- PRICE -->
    <div class="flex-fill">

        <label class="custom-label d-block">
            Price
        </label>

        <input
            type="number"
            step="0.01"
            name="variant_prices[]"
            class="form-control custom-input"
            required
        >

    </div>

    <!-- STOCK -->
    <div class="flex-fill" style="max-width:120px;">

        <label class="custom-label d-block">
            Stock
        </label>

        <input
            type="number"
            name="variant_stocks[]"
            class="form-control custom-input"
            required
        >

    </div>

    <!-- STATUS -->
    <div style="min-width:140px;">

        <label class="custom-label d-block">
            Status
        </label>

        <select
            name="variant_status[]"
            class="form-select custom-input"
        >

            <option value="True">
                Active
            </option>

            <option value="False">
                Inactive
            </option>

        </select>

    </div>

    <!-- DELETE BUTTON -->
    <div>

        <button
            type="button"
            class="btn btn-danger remove-variant-btn"
            style="width:45px;height:45px;"
        >

            <i class="bi bi-trash"></i>

        </button>

    </div>
`;

    variantsContainer.appendChild(variantRow);
});


// =======================
// REMOVE VARIANT
// =======================

variantsContainer.addEventListener("click", function (e) {

    const removeBtn = e.target.closest(".remove-variant-btn");

    if (!removeBtn) return;

    const allRows = document.querySelectorAll(".variant-row");

    // Prevent deleting last variant
    if (allRows.length === 1) {

        alert("At least one variant required");

        return;
    }

    removeBtn.closest(".variant-row").remove();
});

let deletedImages = [];

document.addEventListener("click", function (e) {

    if (
        e.target.closest(".remove-variant-btn")
    ) {

        const rows = document.querySelectorAll(
            ".variant-row"
        );

        if (rows.length <= 1) {

            alert(
                "At least one variant is required."
            );

            return;
        }

        e.target.closest(
            ".variant-row"
        ).remove();
    }
});
// ==============================
// REMOVE EXISTING GALLERY IMAGE
// ==============================

const deletedImagesInput = document.getElementById(
    "deleted-images-input"
);

document.querySelectorAll(
    ".existing-image-remove"
).forEach(button => {

    button.addEventListener("click", function () {

        const imageId = this.dataset.imageId;

        // REMOVE IMAGE PREVIEW

        document.getElementById(
            `gallery-image-${imageId}`
        ).remove();

        // STORE DELETED IDS

        let deletedImages =
            deletedImagesInput.value
            ? deletedImagesInput.value.split(",")
            : [];

        deletedImages.push(imageId);

        deletedImagesInput.value =
            deletedImages.join(",");
    });
});