from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from .models import Order, OrderItem


@staff_member_required(login_url="admin_login")
def admin_orders(request):

    orders = Order.objects.select_related("user").order_by("-created_at")
    search = request.GET.get("search")

    if search:
        orders = orders.filter(
            Q(order_number__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__email__icontains=search)
        )

    status = request.GET.get("status")
    if status:
        orders = orders.filter(status=status)

    payment = request.GET.get("payment")

    if payment:
        orders = orders.filter(payment_method=payment)

    sort = request.GET.get("sort")

    if sort:
        orders = orders.order_by(sort)

    paginator = Paginator(orders, 10)
    page = request.GET.get("page")
    paged_orders = paginator.get_page(page)

    context = {
        "orders": paged_orders,
        "search": search,
        "status": status,
        "payment": payment,
        "sort": sort,
    }

    return render(request, "orders/admin_orders.html", context)


@staff_member_required(login_url="admin_login")
def update_order_status(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        status = request.POST.get("status")

        valid_statuses = [
            "Pending",
            "Confirmed",
            "Shipped",
            "Delivered",
            "Cancelled",
        ]

        if status not in valid_statuses:

            messages.error(request, "Invalid order status.")
            return redirect("admin_orders")

        order.status = status
        order.save()

        messages.success(request, "Order status updated successfully.")
    return redirect("admin_orders")


@staff_member_required(login_url="admin_login")
def admin_order_details(request, order_id):

    order = get_object_or_404(
        Order.objects.select_related("user", "address").prefetch_related(
            "items",
            "items__product",
            "items__variant",
        ),
        id=order_id,
    )

    order_items = order.items.all()

    context = {
        "order": order,
        "order_items": order_items,
    }

    return render(
        request,
        "orders/admin_order_details.html",
        context,
    )


@staff_member_required(login_url="admin_login")
def admin_return_requests(request):

    return_items = (
        OrderItem.objects.filter(return_requested=True)
        .select_related(
            "order",
            "product",
            "variant",
            "order__user",
        )
        .order_by("-id")
    )

    search = request.GET.get("search", "")

    if search:

        return_items = return_items.filter(
            Q(order__order_number__icontains=search)
            | Q(product__name__icontains=search)
            | Q(order__user__first_name__icontains=search)
            | Q(order__user__last_name__icontains=search)
        )

    status = request.GET.get("status", "")

    if status:

        return_items = return_items.filter(return_status=status)

    paginator = Paginator(return_items, 10)

    page = request.GET.get("page")

    paged_returns = paginator.get_page(page)

    context = {
        "return_items": paged_returns,
        "search": search,
        "status": status,
    }

    return render(
        request,
        "orders/returns.html",
        context,
    )


@staff_member_required(login_url="admin_login")
def update_return_status(request, item_id):

    order_item = get_object_or_404(OrderItem, id=item_id)

    if request.method == "POST":

        status = request.POST.get("status")

        valid_statuses = ["Approved", "Rejected"]

        if status not in valid_statuses:

            messages.error(request, "Invalid return status.")

            return redirect(request.META.get("HTTP_REFERER", "admin_return_requests"))

        order_item.return_status = status

        if status == "Approved":

            order_item.variant.stock += order_item.quantity
            order_item.variant.save()

            order_item.status = "Returned"

        order_item.save()

        messages.success(request, f"Return request {status.lower()} successfully.")

    return redirect(request.META.get("HTTP_REFERER", "admin_return_requests"))
