from django.shortcuts import render
from django.views.decorators.cache import never_cache
from store.models import Product
from django.db.models import Min, Q

def home(request):

    latest_products = Product.objects.filter(

        is_deleted=False,
        isBlocked=False,
        isActive=True,
        variants__is_active=True

    ).annotate(

        starting_price=Min(
            'variants__salePrice',
            filter=Q(variants__is_active=True)
        )

    ).distinct().order_by('-createdAt')[:5]

    context = {

        'latest_products': latest_products

    }

    return render(
        request,
        'home.html',
        context
    )
