from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from category.models import Category


@login_required(login_url="admin_login")
def category_management(request):
    if not request.user.is_admin:
        return redirect("home")

    status = request.GET.get("status")
    categories = Category.objects.all()

    if status == "deleted":

        categories = categories.filter(is_deleted=True)
    else:

        categories = categories.filter(is_deleted=False)

    search_query = request.GET.get("q", "")
    if search_query:

        categories = categories.filter(
            Q(category_name__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    total_categories = categories.count()
    active_categories = categories.filter(is_active=True).count()
    archived_categories = categories.filter(is_active=False).count()

    paginator = Paginator(categories, 4)
    page_number = request.GET.get("page")

    try:
        paged_categories = paginator.page(page_number)
    except PageNotAnInteger:

        paged_categories = paginator.page(1)
    except EmptyPage:
        paged_categories = paginator.page(paginator.num_pages)

    context = {
        "categories": paged_categories,
        "total_categories": total_categories,
        "active_categories": active_categories,
        "archived_categories": archived_categories,
        "search_query": search_query,
    }
    return render(request, "admin_panel/category_management.html", context)


@login_required(login_url="admin_login")
def add_category(request):
    if not request.user.is_admin:
        return redirect("home")

    if request.method == "POST":
        category_name = request.POST.get("category_name")
        description = request.POST.get("description")
        slug = request.POST.get("slug")

        if not slug:
            slug = slugify(category_name)

        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request, "A category with this name already exists.")
            return redirect("add_category")

        if Category.objects.filter(slug=slug).exists():
            messages.error(
                request, "This URL slug is already in use. Please choose another."
            )
            return redirect("add_category")

        category = Category.objects.create(
            category_name=category_name,
            slug=slug,
            description=description,
        )
        category.save()
        messages.success(request, "Category added successfully!")
        return redirect("category_management")

    return render(request, "admin_panel/add_category.html")


@login_required(login_url="admin_login")
def edit_category(request, category_slug):
    if not request.user.is_admin:
        return redirect("home")

    category = get_object_or_404(Category, slug=category_slug)

    if request.method == "POST":

        category_name = request.POST.get("category_name", "").strip()
        description = request.POST.get("description", "").strip()
        new_slug = request.POST.get("slug", "").strip()
        status = request.POST.get("status")

        if not category_name:
            messages.error(request, "Category name cannot be empty.")
            return redirect("edit_category", category_slug=category.slug)

        if not new_slug:
            new_slug = slugify(category_name)
        else:
            new_slug = slugify(new_slug)

        if (
            Category.objects.filter(category_name__iexact=category_name)
            .exclude(id=category.id)
            .exists()
        ):
            messages.error(
                request, f'A category named "{category_name}" already exists.'
            )
            return redirect("edit_category", category_slug=category.slug)

        if Category.objects.filter(slug=new_slug).exclude(id=category.id).exists():
            messages.error(
                request, "This URL slug is already in use by another category."
            )
            return redirect("edit_category", category_slug=category.slug)

        category.category_name = category_name
        category.slug = new_slug
        category.description = description

        if status == "active":
            category.is_active = True
        else:
            category.is_active = False
        category.save()
        messages.success(request, "Category updated successfully!")

        return redirect("category_management")

    context = {
        "category": category,
    }
    return render(request, "admin_panel/edit_category.html", context)


@login_required(login_url="admin_login")
def soft_delete_category(request, category_slug):
    if not request.user.is_admin:
        return redirect("home")

    category = get_object_or_404(Category, slug=category_slug)

    category.is_deleted = True
    category.is_active = False
    category.save()

    messages.success(
        request, f'Category "{category.category_name}" was moved to trash.'
    )
    return redirect("category_management")


@login_required(login_url="admin_login")
def restore_category(request, slug):

    if not request.user.is_admin:
        return redirect("home")

    category = get_object_or_404(Category, slug=slug)

    category.is_deleted = False
    category.is_active = True
    category.save()

    messages.success(request, "Category restored successfully.")

    return redirect("category_management")
