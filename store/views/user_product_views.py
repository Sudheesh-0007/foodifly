from django.core.paginator import Paginator
from django.db.models import Q, Min
from store.models import Product
from category.models import Category
from django.shortcuts import render, get_object_or_404, redirect


def shop(request):

    search_query = request.GET.get("q", "")
    sort = request.GET.get("sort")
    category_slug = request.GET.get("category")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    products = (
        Product.objects.filter(
            is_deleted=False, isBlocked=False, isActive=True, variants__is_active=True
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

    categories = Category.objects.filter(is_deleted=False, is_active=True)

    context = {
        "products": paged_products,
        "categories": categories,
        "search_query": search_query,
    }

    return render(request, "store/store.html", context)


def product_detail(request, slug):

    product = get_object_or_404(
        Product.objects.filter(is_deleted=False, isBlocked=False, isActive=True),
        slug=slug,
    )
    variants = product.variants.filter(is_active=True)
    selected_variant = variants.filter(stock__gt=0, is_active=True).first()

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
    context = {
        "product": product,
        "variants": variants,
        "gallery_images": gallery_images,
        "related_products": related_products,
        "selected_variant": selected_variant,
    }

    return render(request, "store/product_detail.html", context)
