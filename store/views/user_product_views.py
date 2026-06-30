from django.core.paginator import Paginator
from django.db.models import Q, Min
from store.models import Product, Variant
from category.models import Category
from wishlist.models import WishlistItem
from django.shortcuts import render, get_object_or_404, redirect
from offers.utils import get_offer_price
from django.http import JsonResponse
from reviews.models import Review

def shop(request):

    search_query = request.GET.get("q", "")
    sort = request.GET.get("sort")
    category_slug = request.GET.get("category")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    products = (
        Product.objects.filter(
            is_deleted=False, isBlocked=False, isActive=True,
            variants__is_active=True,
            category__is_active=True,
            category__is_deleted=False,
        )
        .annotate(starting_price=Min("variants__salePrice"))
        .distinct()
    )

    if search_query:

        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__category_name__icontains=search_query)
            | Q(variants__variant_value__icontains=search_query)
        )

    try:

        if min_price:
            products = products.filter(starting_price__gte=float(min_price))

        if max_price:
            products = products.filter(starting_price__lte=float(max_price))

    except ValueError:
        pass

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if sort == "price_low":
        products = products.order_by("starting_price")

    elif sort == "price_high":
        products = products.order_by("-starting_price")

    elif sort == "a_z":
        products = products.order_by("name")

    elif sort == "z_a":
        products = products.order_by("-name")

    elif sort == "newest":
        products = products.order_by("-createdAt")

    else:
        products = products.order_by("-createdAt")

    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    paged_products = paginator.get_page(page_number)

    for product in paged_products:
        cheapest_variant = (
            product.variants.filter(is_active=True).order_by("salePrice").first()
        )

        if cheapest_variant:

            offer_price, offer = get_offer_price(product, cheapest_variant.salePrice)

            product.original_price = cheapest_variant.salePrice
            product.offer_price = offer_price
            product.offer = offer

    categories = Category.objects.filter(is_deleted=False, is_active=True)

    context = {
        "products": paged_products,
        "categories": categories,
        "search_query": search_query,
    }

    return render(request, "store/store.html", context)


def product_detail(request, slug):

    product = get_object_or_404(
        Product.objects.filter(is_deleted=False, isBlocked=False,
        category__is_active=True,
        category__is_deleted=False,),
        slug=slug,
    )
    variants = product.variants.filter(is_active=True)
    is_available = product.isActive
    selected_variant = variants.filter(stock__gt=0, is_active=True).first()
    offer_price = None
    offer = None

    if selected_variant:

        offer_price, offer = get_offer_price(product, selected_variant.salePrice)

    if not variants.exists():
        return redirect("shop")

    gallery_images = product.gallery_images.all()

    related_products = (
        Product.objects.filter(
            category=product.category,
            is_deleted=False,
            isBlocked=False,
            isActive=True,
            variants__is_active=True,
        )
        .exclude(id=product.id)
        .annotate(
            starting_price=Min(
                "variants__salePrice", filter=Q(variants__is_active=True)
            )
        )
        .distinct()[:4]
    )
    # related_products = (
    #     Product.objects.filter(
    #         category=product.category, is_deleted=False, isBlocked=False, isActive=True
    #     )
    #     .exclude(id=product.id)
    #     .annotate(starting_price=Min("variants__salePrice"))[:4]
    # )
    wishlisted_variant_ids = []

    if request.user.is_authenticated:

        wishlisted_variant_ids = WishlistItem.objects.filter(
            wishlist__user=request.user, product=product
        ).values_list("variant_id", flat=True)

    for related_product in related_products:


        offer_price = None
        offer = None

        if selected_variant:

            offer_price, offer = get_offer_price(product, selected_variant.salePrice)
    reviews = (
        Review.objects.filter(product=product, is_active=True)
        .select_related("user")
        .order_by("-created_at")[:2]
    )
    selected_variant = variants.filter(stock__gt=0, is_active=True).first()

    low_stock = False

    if selected_variant and selected_variant.stock < 5:
        low_stock = True

    context = {
        "product": product,
        "variants": variants,
        "low_stock": low_stock,
        "gallery_images": gallery_images,
        "related_products": related_products,
        "selected_variant": selected_variant,
        "wishlisted_variant_ids": wishlisted_variant_ids,
        "is_available": is_available,
        "offer_price": offer_price,
        "offer": offer,
        "reviews": reviews,
    }

    return render(request, "store/product_detail.html", context)


def get_variant_price(request):

    variant_id = request.GET.get("variant_id")

    try:

        variant = Variant.objects.get(id=variant_id, is_active=True)

        offer_price, offer = get_offer_price(variant.product, variant.salePrice)

        return JsonResponse(
            {
                "success": True,
                "price": str(variant.salePrice),
                "offer_price": str(offer_price),
                "has_offer": offer is not None,
                "discount_type": offer.discount_type if offer else "",
                "discount_value": str(offer.discount_value) if offer else "",
                "stock": variant.stock,
            }
        )

    except Variant.DoesNotExist:

        return JsonResponse({"success": False})
