from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from decimal import Decimal
import uuid
from django.core.paginator import Paginator
from cart.models import Cart, CartItem
from accounts.models import Address
from .models import Order, OrderItem

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Q

import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from wallet.models import Wallet, WalletTransaction
from offers.utils import get_offer_price
from coupon.models import Coupon, CouponUsage


def calculate_grand_total(total, tax, shipping, coupon_discount):

    grand_total = total + tax + shipping - coupon_discount

    if grand_total < 0:

        grand_total = Decimal("0.00")

    return grand_total


def mark_coupon_used(user, coupon):

    if coupon:

        CouponUsage.objects.get_or_create(user=user, coupon=coupon)


def create_order_items(order, cart_items):

    for item in cart_items:

        offer_price, offer = get_offer_price(item.product, item.variant.salePrice)

        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=item.variant,
            quantity=item.quantity,
            price=offer_price,
            total_price=offer_price * item.quantity,
        )

        item.variant.stock -= item.quantity

        item.variant.save()


def get_coupon_details(coupon_code, total):

    coupon = None
    coupon_discount = Decimal("0.00")

    if not coupon_code:

        return coupon, coupon_discount

    try:

        coupon = Coupon.objects.get(code=coupon_code, is_active=True)

        if coupon.discount_type == "PERCENTAGE":

            coupon_discount = (total * coupon.discount_value) / Decimal("100")

        else:

            coupon_discount = coupon.discount_value

    except Coupon.DoesNotExist:

        coupon = None

    return coupon, coupon_discount


@login_required(login_url="login")
def checkout(request):
    total = Decimal("0.00")
    quantity = 0
    tax = Decimal("0.00")
    shipping = Decimal("0.00")
    coupon = None
    coupon_discount = Decimal("0.00")

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).select_related(
            "product", "variant"
        )

        if not cart_items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect("cart")

        addresses = Address.objects.filter(user=request.user).order_by(
            "-is_default", "-id"
        )[:3]

        for item in cart_items:

            if item.variant.stock > 0 and item.quantity > item.variant.stock:

                item.quantity = item.variant.stock

                item.save()

                messages.warning(
                    request,
                    f"{item.product.name} quantity adjusted to available stock.",
                )

        total = Decimal("0.00")
        quantity = 0

        for item in cart_items:

            offer_price, offer = get_offer_price(item.product, item.variant.salePrice)

            item.offer_price = offer_price
            item.offer = offer

            item.total_price = offer_price * item.quantity

            total += item.total_price
            quantity += item.quantity
        print(offer_price)
        print(offer)
        tax = total * Decimal("0.10")

        shipping = Decimal("0.00")

        grand_total = total + tax + shipping

        if request.method == "POST":

            try:
                address_id = request.POST.get("address")
                payment_method = request.POST.get("payment_method")

                coupon_code = request.POST.get("coupon_code")

                coupon, coupon_discount = get_coupon_details(coupon_code, total)

                grand_total = calculate_grand_total(
                    total, tax, shipping, coupon_discount
                )

                amount = int(grand_total * 100)

                if grand_total < 0:
                    grand_total = Decimal("0.00")

                if not address_id:
                    messages.error(request, "Please select a shipping address.")
                    return redirect("checkout")

                if not payment_method:
                    messages.error(request, "Please select a payment method.")
                    return redirect("checkout")

                address = get_object_or_404(Address, id=address_id, user=request.user)

                for item in cart_items:

                    if item.variant.stock <= 0:

                        messages.error(request, f"{item.product.name} is out of stock.")

                        return redirect("cart")

                    if item.quantity > item.variant.stock:

                        item.quantity = item.variant.stock

                        item.save()

                        messages.warning(
                            request,
                            f"{item.product.name} quantity adjusted to available stock.",
                        )

                        return redirect("cart")
                if payment_method == "COD":

                    order = Order.objects.create(
                        user=request.user,
                        address=address,
                        order_number=str(uuid.uuid4()).split("-")[0].upper(),
                        total_amount=total,
                        tax=tax,
                        grand_total=grand_total,
                        is_ordered=True,
                        payment_method="COD",
                        payment_status="Paid",
                        coupon=coupon,
                        coupon_discount=coupon_discount,
                    )

                    coupon, coupon_discount = get_coupon_details(coupon_code, total)
                    create_order_items(order, cart_items)
                    cart_items.delete()
                    mark_coupon_used(request.user, coupon)

                    messages.success(request, "Order placed successfully.")
                    return redirect("order_success", order_id=order.id)

                elif payment_method == "RAZORPAY":
                    client = razorpay.Client(
                        auth=(
                            settings.RAZORPAY_KEY_ID,
                            settings.RAZORPAY_KEY_SECRET,
                        )
                    )

                    payment = client.order.create(
                        {
                            "amount": amount,
                            "currency": "INR",
                            "payment_capture": 1,
                        }
                    )

                    request.session["checkout_data"] = {
                        "address_id": address.id,
                        "coupon_code": coupon_code,
                        "coupon_discount": str(coupon_discount),
                    }

                    context = {
                        "cart_items": cart_items,
                        "addresses": addresses,
                        "total": total,
                        "tax": tax,
                        "shipping": shipping,
                        "grand_total": grand_total,
                        "quantity": quantity,
                        "razorpay_order_id": payment["id"],
                        "razorpay_key": settings.RAZORPAY_KEY_ID,
                        "razorpay_amount": amount,
                    }

                    return render(request, "orders/checkout.html", context)

                elif payment_method == "WALLET":

                    wallet = Wallet.objects.get(user=request.user)

                    if wallet.balance < grand_total:

                        messages.error(request, "Insufficient wallet balance.")

                        return redirect("checkout")

                    wallet.balance -= grand_total

                    wallet.save()

                    order = Order.objects.create(
                        user=request.user,
                        address=address,
                        order_number=str(uuid.uuid4()).split("-")[0].upper(),
                        total_amount=total,
                        tax=tax,
                        grand_total=grand_total,
                        payment_method="WALLET",
                        payment_status="Paid",
                        coupon=coupon,
                        coupon_discount=coupon_discount,
                        status="Confirmed",
                        is_ordered=True,
                    )

                    WalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_type="Debit",
                        amount=grand_total,
                        description=f"Wallet payment for Order #{order.order_number}",
                    )

                    create_order_items(order, cart_items)

                    cart_items.delete()
                    mark_coupon_used(request.user, coupon)

                    messages.success(request, "Order placed using Wallet.")

                    return redirect("order_success", order_id=order.id)

            except Exception as e:

                print("RAZORPAY ERROR:", e)

                messages.error(request, str(e))

                return redirect("checkout")
        wallet, created = Wallet.objects.get_or_create(user=request.user)

        context = {
            "cart_items": cart_items,
            "addresses": addresses,
            "total": total,
            "tax": tax,
            "shipping": shipping,
            "grand_total": grand_total,
            "quantity": quantity,
            "wallet": wallet,
            "coupon": coupon,
            "coupon_discount": coupon_discount,
        }

        return render(request, "orders/checkout.html", context)

    except Cart.DoesNotExist:
        messages.warning(request, "Cart not found.")
        return redirect("shop")

    except Exception as e:
        print("CHECKOUT ERROR:", e)
        messages.error(request, str(e))
        return redirect("cart")


@csrf_exempt
@login_required(login_url="login")
def verify_payment(request):

    if request.method == "POST":

        checkout_data = request.session.get("checkout_data")

        data = json.loads(request.body)

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            )
        )

        try:

            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                }
            )
            checkout_data = request.session.get("checkout_data")

            if not checkout_data:

                return JsonResponse(
                    {
                        "success": False,
                        "error": "Checkout session expired",
                    }
                )

            address = Address.objects.get(
                id=checkout_data["address_id"],
                user=request.user,
            )

            cart = Cart.objects.get(user=request.user)

            cart_items = CartItem.objects.filter(cart=cart)

            total = Decimal("0.00")

            for item in cart_items:

                offer_price, offer = get_offer_price(
                    item.product, item.variant.salePrice
                )

                total += offer_price * item.quantity
            coupon_code = checkout_data.get("coupon_code")

            coupon, coupon_discount = get_coupon_details(coupon_code, total)

            tax = total * Decimal("0.10")

            grand_total = total + tax - coupon_discount

            if grand_total < 0:
                grand_total = Decimal("0.00")

            order = Order.objects.create(
                user=request.user,
                address=address,
                order_number=str(uuid.uuid4()).split("-")[0].upper(),
                total_amount=total,
                tax=tax,
                grand_total=grand_total,
                payment_method="RAZORPAY",
                payment_status="Paid",
                status="Confirmed",
                is_ordered=True,
                coupon=coupon,
                coupon_discount=coupon_discount,
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
            )

            create_order_items(order, cart_items)

            cart_items.delete()
            mark_coupon_used(request.user, coupon)

            if "checkout_data" in request.session:
                del request.session["checkout_data"]

            return JsonResponse(
                {
                    "success": True,
                    "redirect_url": f"/orders/order-success/{order.id}/",
                }
            )

        except Exception as e:

            print("VERIFY PAYMENT ERROR:", e)

            return JsonResponse(
                {
                    "success": False,
                    "error": str(e),
                }
            )

    return JsonResponse(
        {
            "success": False,
            "error": "Invalid request",
        }
    )


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
    total = int(order.total_amount)
    tax = total* Decimal("0.10")
    sub = total + tax
    discount = sub - order.grand_total
    context = {
        "order": order,
        "order_items": order_items,
        "discount": discount,
        'tax':tax
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


@login_required(login_url="login")
def my_orders(request):

    order_items = (
        OrderItem.objects.filter(order__user=request.user)
        .select_related("order", "product", "variant")
        .order_by("-order__created_at")
    )

    search = request.GET.get("search", "")

    if search:

        order_items = order_items.filter(
            Q(order__order_number__icontains=search)
            | Q(product__name__icontains=search)
            | Q(variant__variant_value__icontains=search)
        )

    status = request.GET.get("status", "")

    if status:

        order_items = order_items.filter(order__status=status)

    paginator = Paginator(order_items, 5)

    page = request.GET.get("page")

    paged_orders = paginator.get_page(page)

    context = {
        "order_items": paged_orders,
        "search": search,
        "status": status,
    }

    return render(request, "orders/my_orders.html", context)


@login_required(login_url="login")
def order_details(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    order_items = OrderItem.objects.filter(order=order).select_related(
        "product", "variant"
    )

    context = {
        "order": order,
        "order_items": order_items,
    }

    return render(request, "orders/order_details.html", context)


@login_required(login_url="login")
def cancel_order(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ["Delivered", "Cancelled", "Returned"]:
        messages.error(request, "This order cannot be cancelled.")
        return redirect("order_details", order_id=order.id)

    order.status = "Cancelled"

    order_items = OrderItem.objects.filter(order=order)

    if order.payment_method in ["RAZORPAY", "WALLET"]:
        print("REFUND BLOCK EXECUTED")

        wallet = Wallet.objects.get(user=order.user)
        print("OLD BALANCE:", wallet.balance)
        wallet.balance += order.grand_total

        wallet.save()
        print("NEW BALANCE:", wallet.balance)

        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="Credit",
            amount=order.grand_total,
            description=f"Refund for Order #{order.order_number}",
            transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
        )

    for item in order_items:
        if item.status != "Cancelled":
            item.status = "Cancelled"
            item.save()
            item.variant.stock += item.quantity
            item.variant.save()

    order.save()

    messages.success(request, "Order cancelled successfully.")
    return redirect("order_details", order_id=order.id)


@login_required(login_url="login")
def cancel_order_item(request, item_id):

    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    order = order_item.order

    if order_item.status == "Cancelled":
        messages.error(request, "This item is already cancelled.")
        return redirect("order_details", order_id=order.id)

    if order.status in ["Shipped", "Delivered"]:
        messages.error(request, "This item cannot be cancelled now.")
        return redirect("order_details", order_id=order.id)

    order_item.status = "Cancelled"
    order_item.save()
    if order.payment_method in ["RAZORPAY", "WALLET"]:

        refund_amount = order_item.total_price

        wallet = Wallet.objects.get(user=order.user)

        item_tax = order_item.total_price * Decimal("0.10")

        refund_amount = order_item.total_price + item_tax
        wallet.balance += refund_amount

        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="Credit",
            amount=refund_amount,
            description=f"Refund for cancelled item - {order_item.product.name}",
            transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
        )
    variant = order_item.variant
    variant.stock += order_item.quantity
    variant.save()

    active_items = OrderItem.objects.filter(order=order, status="Active")

    subtotal = sum(item.total_price for item in active_items)
    tax = subtotal * Decimal("0.10")
    grand_total = subtotal + tax - order.coupon_discount

    if grand_total < 0:

        grand_total = Decimal("0.00")
        
    order.total_amount = subtotal
    order.tax = tax
    order.grand_total = grand_total

    if not active_items.exists():
        order.status = "Cancelled"
        if order.payment_method in ["RAZORPAY", "WALLET"]:
            order.payment_status = "Refunded"
    order.save()

    messages.success(request, "Item cancelled successfully.")
    return redirect("order_details", order_id=order.id)


@login_required(login_url="login")
def request_return(request, item_id):

    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)

    if order_item.order.status not in ["Delivered", "Returned"]:
        messages.error(request, "Only delivered items can be returned.")
        return redirect("order_details", order_id=order_item.order.id)

    if order_item.return_requested:
        messages.warning(request, "Return already requested.")
        return redirect("order_details", order_id=order_item.order.id)

    if request.method == "POST":
        reason = request.POST.get("reason")
        order_item.return_requested = True
        order_item.return_reason = reason
        order_item.return_status = "Requested"
        order_item.save()

        messages.success(request, "Return request submitted successfully.")
    return redirect("order_details", order_id=order_item.order.id)


@login_required(login_url="login")
def payment_failed(request):

    error = request.GET.get("error")
    order_id = request.GET.get("order_id")

    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)

            order.payment_status = "Failed"
            order.status = "Failed"
            order.save()

        except Order.DoesNotExist:
            pass

    context = {"error": error}

    return render(request, "orders/payment_failed.html", context)
