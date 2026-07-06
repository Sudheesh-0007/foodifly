from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect

from orders.models import OrderItem
from store.models import Product

from .models import Review


@login_required(login_url="login")
def submit_review(request, product_id):

    if request.method != "POST":
        return redirect("shop")

    product = get_object_or_404(Product, id=product_id)

    purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__status="Delivered",
        product=product,
    ).exists()

    if not purchased:

        messages.error(request, "You can review only purchased products.")

        return redirect(
            "product_detail",
            slug=product.slug,
        )

    rating = request.POST.get("rating")
    review_text = request.POST.get("review")

    if not rating:

        messages.error(request, "Please select a rating.")

        return redirect(
            "product_detail",
            slug=product.slug,
        )

    try:

        rating = int(rating)

        if rating < 1 or rating > 5:

            messages.error(request, "Rating must be between 1 and 5.")

            return redirect(
                "product_detail",
                slug=product.slug,
            )

    except ValueError:

        messages.error(request, "Invalid rating.")

        return redirect(
            "product_detail",
            slug=product.slug,
        )

    review, created = Review.objects.update_or_create(
        user=request.user,
        product=product,
        defaults={
            "rating": rating,
            "review": review_text,
        },
    )
    average_rating = (
        Review.objects.filter(product=product, is_active=True).aggregate(
            avg=Avg("rating")
        )["avg"]
        or 0
    )
    review_count = Review.objects.filter(product=product, is_active=True).count()
    product.averageRating = round(average_rating, 1)

    product.reviewCount = review_count

    product.save()

    if created:

        messages.success(request, "Review submitted successfully.")

    else:

        messages.success(request, "Review updated successfully.")

    return redirect(
        "product_detail",
        slug=product.slug,
    )
