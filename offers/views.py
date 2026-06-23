from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from category.models import Category
from offers.models import Offer
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q


@staff_member_required(login_url="admin_login")
def offer_list(request):

    offers = Offer.objects.all()

    search = request.GET.get("search", "")

    if search:
        offers = offers.filter(
            Q(name__icontains=search)
            | Q(product__name__icontains=search)
            | Q(category__category_name__icontains=search)
        )

    offer_type = request.GET.get("type", "")

    if offer_type:
        offers = offers.filter(offer_type=offer_type)

    sort = request.GET.get("sort", "newest")

    if sort == "newest":
        offers = offers.order_by("-created_at")

    elif sort == "oldest":
        offers = offers.order_by("created_at")

    elif sort == "name_asc":
        offers = offers.order_by("name")

    elif sort == "name_desc":
        offers = offers.order_by("-name")

    paginator = Paginator(offers, 5)

    page = request.GET.get("page")

    offers = paginator.get_page(page)

    context = {
        "offers": offers,
        "search": search,
        "sort": sort,
        "offer_type": offer_type,
    }

    return render(request, "offer/admin_offers.html", context)


@staff_member_required(login_url="admin_login")
def add_offer(request):

    products = Product.objects.filter(isActive=True, isBlocked=False, is_deleted=False)

    categories = Category.objects.all()

    if request.method == "POST":

        name = request.POST.get("name")

        offer_type = request.POST.get("offer_type")

        discount_type = request.POST.get("discount_type")

        discount_value = request.POST.get("discount_value")

        start_date = request.POST.get("start_date")

        end_date = request.POST.get("end_date")

        product_id = request.POST.get("product")

        category_id = request.POST.get("category")

        offer = Offer(
            name=name,
            offer_type=offer_type,
            discount_type=discount_type,
            discount_value=discount_value,
            start_date=start_date,
            end_date=end_date,
        )

        if offer_type == "PRODUCT":

            offer.product_id = product_id

        elif offer_type == "CATEGORY":

            offer.category_id = category_id

        offer.save()

        messages.success(request, "Offer created successfully.")

        return redirect("offer_management")

    context = {
        "products": products,
        "categories": categories,
    }

    return render(
        request,
        "offer/create_offer.html",
        context,
    )


@staff_member_required(login_url="admin_login")
def edit_offer(request, offer_id):

    offer = get_object_or_404(Offer, id=offer_id)

    products = Product.objects.filter(isActive=True, isBlocked=False, is_deleted=False)

    categories = Category.objects.all()

    if request.method == "POST":

        offer.name = request.POST.get("name")
        offer.offer_type = request.POST.get("offer_type")
        offer.discount_type = request.POST.get("discount_type")
        offer.discount_value = request.POST.get("discount_value")
        offer.start_date = request.POST.get("start_date")
        offer.end_date = request.POST.get("end_date")
        if offer.offer_type == "PRODUCT":

            product_id = request.POST.get("product")

            if not product_id:
                messages.error(request, "Please select a product.")
                return redirect("edit_offer", offer_id=offer.id)

            offer.product_id = product_id
            offer.category = None

        elif offer.offer_type == "CATEGORY":

            category_id = request.POST.get("category")

            if not category_id:
                messages.error(request, "Please select a category.")
                return redirect("edit_offer", offer_id=offer.id)

            offer.category_id = category_id
            offer.product = None
        offer.is_active = request.POST.get("is_active") == "on"

        offer.save()

        messages.success(request, "Offer updated successfully.")

        return redirect("offer_management")

    context = {
        "offer": offer,
        "products": products,
        "categories": categories,
    }

    return render(request, "offer/edit_offer.html", context)


@staff_member_required(login_url="admin_login")
def toggle_offer_status(request, offer_id):

    offer = get_object_or_404(Offer, id=offer_id)

    offer.is_active = not offer.is_active

    offer.save()

    messages.success(request, f"{offer.name} status updated successfully.")

    return redirect("offer_management")
