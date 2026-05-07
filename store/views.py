from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q , Sum, Min
from django.contrib import messages
from .models import Product, Variant, ProductGallery
from category.models import Category
from django.utils.text import slugify


@login_required(login_url='admin_login')
def product_management(request):

    if not request.user.is_admin:
        return redirect('home')
    
    status = request.GET.get('status')
    search_query = request.GET.get('q', '')
    sort = request.GET.get('sort')

    products = Product.objects.prefetch_related('variants').annotate(total_stock=Sum(
            'variants__stock',
            filter=Q(variants__is_active=True)
        ),
        starting_price=Min('variants__salePrice',filter=Q(variants__is_active=True)))

    if status == 'deleted':
        products = products.filter(is_deleted=True)
    elif status == 'published':
        products = products.filter(is_deleted=False,isActive=True)

    else:
        products = products.filter(is_deleted=False)

    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    if sort == 'price_low':
        products = products.order_by('starting_price')

    elif sort == 'price_high':
        products = products.order_by('-starting_price')

    elif sort == 'name_asc':

        products = products.order_by('name')

    elif sort == 'name_desc':

        products = products.order_by('-name')
    else:
        products = products.order_by('-id')

    total_products = Product.objects.filter(is_deleted=False).count()

    active_products = Product.objects.filter(is_deleted=False,isActive=True).count()

    out_of_stock = Product.objects.annotate(active_stock=Sum('variants__stock')).filter(is_deleted=False).filter(
        Q(active_stock__lte=0) |
        Q(active_stock__isnull=True)).count()

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    paged_products = paginator.get_page(page_number)

    context = {

        'products': paged_products,

        'total_products': total_products,

        'active_products': active_products,

        'out_of_stock': out_of_stock,

        'search_query': search_query,
    }
    return render(request,'admin_panel/product_management.html',context)

def add_product(request):

    categories = Category.objects.filter(is_active=True,is_deleted=False)
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        images = request.FILES.getlist('images')

        if len(images) < 3:
            messages.error(request, "Minimum 3 images required.")
            return redirect('add_product')

        if Product.objects.filter(slug=slug).exists():
            messages.error(request, "Slug already exists.")
            return redirect('add_product')
        
        category = Category.objects.get(id=category_id)
        main_image = images[0] 

        product = Product.objects.create(
            category=category,
            name=name,
            slug=slugify(slug),
            description=description,
            image=main_image,
            isActive=is_active,
        )

        for index, image in enumerate(images):
            ProductGallery.objects.create(
                product=product,
                image=image,
                is_main=(index == 0)
            )
        variant_values = request.POST.getlist('variant_values[]')
        variant_prices = request.POST.getlist('variant_prices[]')
        variant_stocks = request.POST.getlist('variant_stocks[]')
        variant_status = request.POST.getlist('variant_status[]')

        for vvalue, vprice, vstock,status in zip(
            variant_values,
            variant_prices,
            variant_stocks,
            variant_status,
        ):  
            Variant.objects.create(
                    product=product,
                    variant_value=vvalue,
                    salePrice=vprice,
                    stock=vstock,
                    is_active=(status == "True")
                )

        messages.success(request, "Product added successfully!")
        return redirect('add_product')

    context = {
        'categories': categories,
    }

    return render(request, 'admin_panel/add_product.html', context)


@login_required(login_url='admin_login')
def edit_product(request, product_id):

    if not request.user.is_admin:
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)

    categories = Category.objects.filter(is_deleted=False)

    variants = product.variants.all()

    gallery_images = product.gallery_images.all()

    if request.method == 'POST':

        product.name = request.POST.get('name')

        product.slug = request.POST.get('slug')

        product.description = request.POST.get('description')

        category_id = request.POST.get('category')

        product.category = Category.objects.get(id=category_id)

        product.isActive = (request.POST.get('is_active') == 'on')
        images = request.FILES.getlist('images')
        if images:
            product.image = images[0]
        product.save()
        product.variants.all().delete()
        variant_values = request.POST.getlist('variant_values[]')
        variant_prices = request.POST.getlist('variant_prices[]')
        variant_stocks = request.POST.getlist('variant_stocks[]')
        variant_statuses = request.POST.getlist('variant_status[]')

        for value, price, stock, status in zip(variant_values,variant_prices,variant_stocks,variant_statuses,):
            Variant.objects.create(
                product=product,
                variant_value=value,
                salePrice=price,
                stock=stock,
                is_active=(status == "True")
            )
        has_active_variant = product.variants.filter(is_active=True).exists()
        product.isActive = has_active_variant
        product.save()   

        if images:
            product.gallery_images.all().delete()
            for index, image in enumerate(images):
                ProductGallery.objects.create(
                    product=product,
                    image=image,
                    is_main=(index == 0)
                )

        messages.success(request,"Product updated successfully")
        return redirect('admin_products')

    context = {

        'product': product,
        'categories': categories,
        'variants': variants,
        'gallery_images': gallery_images,
    }

    return render(request,'admin_panel/edit_product.html',context)


@login_required(login_url='admin_login')
def delete_product(request, product_id):
    if not request.user.is_admin:
        return redirect('home')
    product = get_object_or_404(Product,id=product_id,is_deleted=False)
    product.is_deleted = True
    product.isActive = False
    product.save()
    product.variants.update(is_active=False)

    messages.success(request,"Product deleted successfully.")
    return redirect('admin_products')

@login_required(login_url='admin_login')
def restore_product(request, product_id):
    if not request.user.is_admin:
        return redirect('home')

    product = get_object_or_404(Product,id=product_id)
    product.is_deleted = False
    product.isActive = True
    product.save()

    messages.success(request,"Product restored successfully.")
    return redirect('admin_products')