from django.shortcuts import render, redirect, get_object_or_404
from .models import Coupon
from decimal import Decimal
from django.http import JsonResponse
from django.utils import timezone
from .models import Coupon, CouponUsage
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator


@staff_member_required(login_url="admin_login")
def coupon_list(request):

    today = timezone.now().date()

    search = request.GET.get("search", "")
    status = request.GET.get("status", "")

    coupons_queryset = Coupon.objects.filter(is_deleted=False).order_by("-id")

    if search:

        coupons_queryset = coupons_queryset.filter(
            Q(code__icontains=search) | Q(discount_type__icontains=search)
        )

    if status == "active":

        coupons_queryset = coupons_queryset.filter(is_active=True, valid_to__gte=today)

    elif status == "expired":

        coupons_queryset = coupons_queryset.filter(valid_to__lt=today)

    elif status == "inactive":

        coupons_queryset = coupons_queryset.filter(is_active=False)

    paginator = Paginator(coupons_queryset, 7)

    page = request.GET.get("page")

    coupons = paginator.get_page(page)

    context = {
        "coupons": coupons,
        "search": search,
        "status": status,
        "total_coupons": Coupon.objects.count(),
        "active_coupons": Coupon.objects.filter(
            is_active=True, valid_to__gte=today
        ).count(),
        "expired_coupons": Coupon.objects.filter(valid_to__lt=today).count(),
    }

    return render(
        request,
        "admin_panel/coupon/coupon_list.html",
        context,
    )


def add_coupon(request):

    if request.method == "POST":

        code = request.POST.get("code", "").strip().upper()
        discount_type = request.POST.get("discount_type")
        discount_value = request.POST.get("discount_value")
        minimum_amount = request.POST.get("minimum_amount")
        maximum_discount = request.POST.get("maximum_discount")
        valid_from = request.POST.get("valid_from")
        valid_to = request.POST.get("valid_to")

        if Coupon.objects.filter(code=code).exists():

            messages.error(request, "Coupon code already exists.")

            return redirect("add_coupon")

        if Decimal(discount_value) <= 0:

            messages.error(request, "Discount value must be greater than zero.")

            return redirect("add_coupon")

        if Decimal(minimum_amount) <= 0:

            messages.error(request, "Minimum amount must be greater than zero.")

            return redirect("add_coupon")

        if maximum_discount:

            if Decimal(maximum_discount) <= 0:

                messages.error(request, "Maximum discount must be greater than zero.")

                return redirect("add_coupon")

        if valid_from >= valid_to:

            messages.error(request, "Valid To date must be after Valid From date.")

            return redirect("add_coupon")

        Coupon.objects.create(
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            minimum_amount=minimum_amount,
            maximum_discount=maximum_discount or None,
            valid_from=valid_from,
            valid_to=valid_to,
            is_active=True,
        )

        messages.success(request, "Coupon created successfully.")

        return redirect("coupon_list")

    return render(
        request,
        "admin_panel/coupon/add_coupon.html",
    )


@login_required
def apply_coupon(request):

    code = request.GET.get("coupon_code")

    total = Decimal(request.GET.get("total", "0"))

    try:

        coupon = Coupon.objects.get(code=code.upper(), is_active=True)

    except Coupon.DoesNotExist:

        return JsonResponse({"success": False, "message": "Invalid coupon code."})

    today = timezone.now().date()

    if coupon.valid_from > today:

        return JsonResponse({"success": False, "message": "Coupon not active yet."})

    if coupon.valid_to < today:

        return JsonResponse({"success": False, "message": "Coupon expired."})

    if total < coupon.minimum_amount:

        return JsonResponse(
            {
                "success": False,
                "message": f"Minimum order amount ₹{coupon.minimum_amount}",
            }
        )

    already_used = CouponUsage.objects.filter(user=request.user, coupon=coupon).exists()

    if already_used:

        return JsonResponse({"success": False, "message": "Coupon already used."})

    if coupon.discount_type == "PERCENTAGE":

        discount = (total * coupon.discount_value) / 100

        if coupon.maximum_discount:

            discount = min(discount, coupon.maximum_discount)

    else:

        discount = coupon.discount_value

    tax = total * Decimal("0.10")

    grand_total = total + tax - discount

    return JsonResponse(
        {
            "success": True,
            "discount": float(discount),
            "grand_total": float(grand_total),
            "coupon_code": coupon.code,
            "message": "Coupon applied successfully.",
        }
    )


def edit_coupon(request, coupon_id):

    coupon = get_object_or_404(Coupon, id=coupon_id)

    if request.method == "POST":

        code = request.POST.get("code", "").strip().upper()
        discount_type = request.POST.get("discount_type")
        discount_value = request.POST.get("discount_value")
        minimum_amount = request.POST.get("minimum_amount")
        maximum_discount = request.POST.get("maximum_discount")
        valid_from = request.POST.get("valid_from")
        valid_to = request.POST.get("valid_to")

        if Coupon.objects.filter(code=code).exclude(id=coupon.id).exists():

            messages.error(request, "Coupon code already exists.")

            return redirect("edit_coupon", coupon.id)

        if Decimal(discount_value) <= 0:

            messages.error(request, "Discount value must be greater than zero.")

            return redirect("edit_coupon", coupon.id)

        if Decimal(minimum_amount) <= 0:

            messages.error(request, "Minimum amount must be greater than zero.")

            return redirect("edit_coupon", coupon.id)

        if maximum_discount:

            if Decimal(maximum_discount) <= 0:

                messages.error(request, "Maximum discount must be greater than zero.")

                return redirect("edit_coupon", coupon.id)

        if valid_from >= valid_to:

            messages.error(request, "Valid To must be greater than Valid From.")

            return redirect("edit_coupon", coupon.id)

        coupon.code = code
        coupon.discount_type = discount_type
        coupon.discount_value = discount_value
        coupon.minimum_amount = minimum_amount
        coupon.maximum_discount = maximum_discount or None
        coupon.valid_from = valid_from
        coupon.valid_to = valid_to

        coupon.save()

        messages.success(request, "Coupon updated successfully.")

        return redirect("coupon_list")

    context = {
        "coupon": coupon,
    }

    return render(
        request,
        "admin_panel/coupon/edit_coupon.html",
        context,
    )


def toggle_coupon_status(request, coupon_id):

    coupon = get_object_or_404(Coupon, id=coupon_id)

    coupon.is_active = not coupon.is_active

    coupon.save()

    if coupon.is_active:

        messages.success(request, "Coupon activated successfully.")

    else:

        messages.success(request, "Coupon deactivated successfully.")

    return redirect("coupon_list")
