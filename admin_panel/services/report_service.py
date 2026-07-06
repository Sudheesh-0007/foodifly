import calendar
from datetime import datetime, timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from accounts.models import Account
from category.models import Category
from coupon.models import Coupon
from orders.models import Order, OrderItem
from store.models import Product


def get_filtered_orders(filter_type, start_date=None, end_date=None):

    today = timezone.now()
    # only deliverd product is showing in sales report if you want add pending , shipped, conformed
    orders = Order.objects.filter(status="Delivered", payment_status="Paid")

    if start_date and end_date:

        orders = orders.filter(created_at__date__range=[start_date, end_date])

        return orders

    if filter_type == "daily":

        orders = orders.filter(created_at__date=today.date())

    elif filter_type == "weekly":

        orders = orders.filter(created_at__gte=today - timedelta(days=7))

    elif filter_type == "monthly":

        orders = orders.filter(
            created_at__year=today.year, created_at__month=today.month
        )

    elif filter_type == "yearly":

        orders = orders.filter(created_at__year=today.year)

    return orders


def get_sales_summary(orders):

    total_sales = orders.aggregate(total=Sum("grand_total"))["total"] or 0

    total_orders = orders.count()

    total_users = Account.objects.count()

    total_products = Product.objects.filter(is_deleted=False).count()

    total_categories = Category.objects.filter(is_deleted=False).count()

    total_coupons = Coupon.objects.count()

    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_products": total_products,
        "total_categories": total_categories,
        "total_coupons": total_coupons,
    }


def get_recent_orders(orders, limit=5):

    return orders.select_related("user").order_by("-created_at")[:limit]


def get_best_selling_products(orders, limit=5):

    return (
        OrderItem.objects.filter(order__in=orders)
        .values("product__name")
        .annotate(total_sold=Sum("quantity"), revenue=Sum("total_price"))
        .order_by("-total_sold")[:limit]
    )


def get_best_selling_categories(orders, limit=5):

    return (
        OrderItem.objects.filter(order__in=orders)
        .values("product__category__category_name")
        .annotate(total_sold=Sum("quantity"), revenue=Sum("total_price"))
        .order_by("-total_sold")[:limit]
    )


def get_sales_chart_data(filter_type, start_date=None, end_date=None):

    labels = []
    values = []

    today = timezone.now()

    orders = get_sales_report_orders(filter_type, start_date, end_date)

    if start_date and end_date:

        start = datetime.strptime(start_date, "%Y-%m-%d").date()

        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        current = start

        while current <= end:

            revenue = (
                orders.filter(created_at__date=current).aggregate(
                    total=Sum("grand_total")
                )["total"]
                or 0
            )

            labels.append(current.strftime("%d %b"))

            values.append(float(revenue))

            current += timedelta(days=1)

        return {
            "chart_labels": labels,
            "chart_values": values,
        }

    if filter_type == "daily":

        for hour in range(24):

            revenue = (
                orders.filter(created_at__hour=hour).aggregate(
                    total=Sum("grand_total")
                )["total"]
                or 0
            )

            labels.append(f"{hour}:00")
            values.append(float(revenue))

    elif filter_type == "weekly":

        for i in range(6, -1, -1):

            day = today - timedelta(days=i)

            revenue = (
                orders.filter(created_at__date=day.date()).aggregate(
                    total=Sum("grand_total")
                )["total"]
                or 0
            )

            labels.append(day.strftime("%a"))

            values.append(float(revenue))

    elif filter_type == "monthly":
        days_in_month = calendar.monthrange(today.year, today.month)[1]

        for day in range(1, days_in_month + 1):

            revenue = (
                orders.filter(created_at__day=day).aggregate(total=Sum("grand_total"))[
                    "total"
                ]
                or 0
            )

            labels.append(str(day))
            values.append(float(revenue))

    elif filter_type == "yearly":

        months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

        for month in range(1, 13):

            revenue = (
                orders.filter(created_at__month=month).aggregate(
                    total=Sum("grand_total")
                )["total"]
                or 0
            )

            labels.append(months[month - 1])
            values.append(float(revenue))

    return {
        "chart_labels": labels,
        "chart_values": values,
    }


def get_payment_distribution(orders):

    data = (
        orders.values("payment_method")
        .annotate(total=Sum("grand_total"))
        .order_by("-total")
    )

    labels = []
    values = []

    for item in data:

        labels.append(item["payment_method"])
        values.append(float(item["total"]))

    return {
        "payment_labels": labels,
        "payment_values": values,
    }


def get_order_status_distribution(orders):

    data = orders.values("status").annotate(count=Count("id"))
    print("STATUS DATA:", list(data))

    labels = []
    values = []

    for item in data:

        labels.append(item["status"])
        values.append(item["count"])

    return {
        "status_labels": labels,
        "status_values": values,
    }


def get_sales_report_orders(filter_type, start_date=None, end_date=None):

    today = timezone.now()

    orders = Order.objects.all()

    if start_date and end_date:

        return orders.filter(created_at__date__range=[start_date, end_date])

    if filter_type == "daily":

        orders = orders.filter(created_at__date=today.date())

    elif filter_type == "weekly":

        orders = orders.filter(created_at__gte=today - timedelta(days=7))

    elif filter_type == "monthly":

        orders = orders.filter(
            created_at__year=today.year, created_at__month=today.month
        )

    elif filter_type == "yearly":

        orders = orders.filter(created_at__year=today.year)

    return orders
