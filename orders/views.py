from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from decimal import Decimal
import uuid

from cart.models import Cart, CartItem
from accounts.models import Address
from .models import Order, OrderItem

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


@login_required(login_url="login")
def checkout(request):

    total = Decimal("0.00")
    quantity = 0
    tax = Decimal("0.00")
    shipping = Decimal("0.00")

    try:

        cart = Cart.objects.get(user=request.user)

        cart_items = CartItem.objects.filter(cart=cart).select_related(
            "product", "variant"
        )

        if not cart_items.exists():

            messages.warning(request, "Your cart is empty.")

            return redirect("cart")

        for item in cart_items:

            item.total_price = item.variant.salePrice * item.quantity

            total += item.total_price

            quantity += item.quantity

        tax = total * Decimal("0.10")

        shipping = Decimal("0.00")

        grand_total = total + tax + shipping

        addresses = Address.objects.filter(user=request.user).order_by(
            "-is_default", "-id"
        )[:3]

        if request.method == "POST":

            try:

                address_id = request.POST.get("address")

                payment_method = request.POST.get("payment_method")

                if not address_id:

                    messages.error(request, "Please select a shipping address.")

                    return redirect("checkout")

                if not payment_method:

                    messages.error(request, "Please select a payment method.")

                    return redirect("checkout")

                address = get_object_or_404(Address, id=address_id, user=request.user)

                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    order_number=str(uuid.uuid4()).split("-")[0].upper(),
                    total_amount=total,
                    tax=tax,
                    grand_total=grand_total,
                    payment_method=payment_method,
                    is_ordered=True,
                )

                for item in cart_items:

                    if item.quantity > item.variant.stock:

                        messages.error(
                            request, f"Sorry, {item.product.name} is out of stock."
                        )

                        order.delete()

                        return redirect("checkout")

                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        variant=item.variant,
                        quantity=item.quantity,
                        price=item.variant.salePrice,
                        total_price=(item.variant.salePrice * item.quantity),
                    )

                    item.variant.stock -= item.quantity

                    item.variant.save()

                cart_items.delete()

                messages.success(request, "Order placed successfully.")

                return redirect("order_success", order_id=order.id)

            except Exception as e:

                messages.error(request, "Order placement failed. Please try again.")

                return redirect("checkout")

        context = {
            "cart_items": cart_items,
            "addresses": addresses,
            "total": total,
            "tax": tax,
            "shipping": shipping,
            "grand_total": grand_total,
            "quantity": quantity,
        }

        return render(request, "orders/checkout.html", context)

    except Cart.DoesNotExist:

        messages.warning(request, "Cart not found.")

        return redirect("shop")

    except Exception as e:

        messages.error(request, "Something went wrong. Please try again.")

        return redirect("cart")

    except Cart.DoesNotExist:

        messages.warning(request, "Cart not found.")

        return redirect("shop")


@login_required(login_url="login")
def order_success(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    context = {"order": order}

    return render(request, "orders/order_success.html", context)




@login_required(login_url="login")
def download_invoice(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    order_items = OrderItem.objects.filter(order=order)

    template_path = "orders/invoice.html"

    context = {
        "order": order,
        "order_items": order_items,
    }

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = (
        f'attachment; filename="invoice_{order.order_number}.pdf"'
    )

    template = get_template(template_path)

    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:

        return HttpResponse("Error generating invoice")

    return response
