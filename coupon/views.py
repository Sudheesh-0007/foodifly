from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Coupon, CouponUsage

from decimal import Decimal
from datetime import datetime, date

def validate_coupon_data(request, form_data, coupon=None):
    context = {"form_data": form_data}

    code = form_data.get("code", "").strip().upper()
    discount_type = form_data.get("discount_type")
    discount_value = form_data.get("discount_value")
    minimum_amount = form_data.get("minimum_amount")
    maximum_discount = form_data.get("maximum_discount")
    valid_from = form_data.get("valid_from")
    valid_to = form_data.get("valid_to")

    if not code:
        return False, "Coupon code is required.", context

    duplicate = Coupon.objects.filter(code__iexact=code)

    if coupon:
        duplicate = duplicate.exclude(id=coupon.id)

    if duplicate.exists():
        return False, "Coupon code already exists.", context

    try:
        discount_value = Decimal(discount_value)
        minimum_amount = Decimal(minimum_amount)
        maximum_discount = (
            Decimal(maximum_discount)
            if maximum_discount else None
        )
    except:
        return False, "Please enter valid numeric values.", context

    if discount_value <= 0:
        return False, "Discount value must be greater than zero.", context

    if minimum_amount <= 0:
        return False, "Minimum purchase amount must be greater than zero.", context

    if maximum_discount and maximum_discount <= 0:
        return False, "Maximum discount must be greater than zero.", context

    if discount_type == "PERCENTAGE" and discount_value > Decimal("100"):
        return False, "Percentage discount cannot exceed 100%.", context

    if (
        discount_type == "FIXED"
        and minimum_amount <= discount_value
    ):
        return (
            False,
            "For a flat amount coupon, the minimum purchase amount must be greater than the discount amount.",
            context,
        )

    try:
        valid_from = datetime.strptime(valid_from, "%Y-%m-%d").date()
        valid_to = datetime.strptime(valid_to, "%Y-%m-%d").date()
    except ValueError:
        return False, "Please enter valid dates.", context

    if valid_from < date.today():
        return False, "Valid From date cannot be in the past.", context

    if valid_to <= valid_from:
        return False, "Valid To date must be after Valid From date.", context

    cleaned_data = {
        "code": code,
        "discount_type": discount_type,
        "discount_value": discount_value,
        "minimum_amount": minimum_amount,
        "maximum_discount": maximum_discount,
        "valid_from": valid_from,
        "valid_to": valid_to,
    }

    return True, cleaned_data, context

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

        is_valid, result, context = validate_coupon_data(
            request,
            request.POST,
        )

        if not is_valid:
            messages.error(request, result)
            return render(
                request,
                "admin_panel/coupon/add_coupon.html",
                context,
            )

        Coupon.objects.create(
            **result,
            is_active=True,
        )

        messages.success(request, "Coupon created successfully.")
        return redirect("coupon_list")

    return render(request, "admin_panel/coupon/add_coupon.html")

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
    request.session["checkout_data"] = {
        **request.session.get("checkout_data", {}),
        "coupon_code": coupon.code,
    }
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

        is_valid, result, context = validate_coupon_data(
            request,
            request.POST,
            coupon=coupon,
        )

        if not is_valid:
            messages.error(request, result)
            return render(
                request,
                "admin_panel/coupon/edit_coupon.html",
                {
                    "coupon": coupon,
                    **context,
                },
            )

        coupon.code = result["code"]
        coupon.discount_type = result["discount_type"]
        coupon.discount_value = result["discount_value"]
        coupon.minimum_amount = result["minimum_amount"]
        coupon.maximum_discount = result["maximum_discount"]
        coupon.valid_from = result["valid_from"]
        coupon.valid_to = result["valid_to"]

        coupon.save()

        messages.success(request, "Coupon updated successfully.")
        return redirect("coupon_list")
    return render(request,"admin_panel/coupon/edit_coupon.html",{"coupon": coupon,},)


def toggle_coupon_status(request, coupon_id):

    coupon = get_object_or_404(Coupon, id=coupon_id)

    coupon.is_active = not coupon.is_active

    coupon.save()

    if coupon.is_active:

        messages.success(request, "Coupon activated successfully.")

    else:

        messages.success(request, "Coupon deactivated successfully.")

    return redirect("coupon_list")
