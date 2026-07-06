function increaseQuantity(cartItemId) {

    fetch(`/cart/increase/${cartItemId}/`)
        .then(response => response.json())
        .then(data => {

            if (data.success) {

                document.getElementById(
                    `qty-${cartItemId}`
                ).innerText = data.quantity;

                document.getElementById(
                    `item-total-${cartItemId}`
                ).innerText = "₹" + data.item_total;

                updateCartSummary(data);

            } else {

                alert(data.message);

            }

        });

}


function decreaseQuantity(cartItemId) {

    fetch(`/cart/decrease/${cartItemId}/`)
        .then(response => response.json())
        .then(data => {

            if (data.success) {

                if (data.deleted) {

                    location.reload();
                    

                } else {

                    document.getElementById(
                        `qty-${cartItemId}`
                    ).innerText = data.quantity;

                    document.getElementById(
                        `item-total-${cartItemId}`
                    ).innerText = "₹" + data.item_total;

                    updateCartSummary(data);

                }

            }

        });

}


function removeCartItem(cartItemId) {

    fetch(`/cart/remove/${cartItemId}/`)
        .then(response => response.json())
        .then(data => {

            if (data.success) {

                document.getElementById(
                    `cart-item-${cartItemId}`
                ).remove();

                updateCartSummary(data);

                if (data.cart_items == 0) {

                    location.reload();

                }

            }

        });

}


function updateCartSummary(data) {

    document.getElementById(
        "cart-subtotal"
    ).innerText = "₹" + data.subtotal;

    document.getElementById(
        "cart-tax"
    ).innerText = "₹" + data.tax;

    document.getElementById(
        "cart-grand-total"
    ).innerText = "₹" + data.grand_total;

    document.getElementById(
        "cart-items"
    ).innerText = data.cart_items;

}