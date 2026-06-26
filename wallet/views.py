from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet, WalletTransaction
from django.core.paginator import Paginator

from django.core.paginator import Paginator
from wallet.models import Wallet, WalletTransaction


@login_required(login_url="login")
def wallet_view(request):

    wallet, created = Wallet.objects.get_or_create(user=request.user)

    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by(
        "-created_at"
    )

    transaction_type = request.GET.get("type")

    if transaction_type:

        transactions = transactions.filter(transaction_type=transaction_type)

    paginator = Paginator(transactions, 10)

    page = request.GET.get("page")

    transactions = paginator.get_page(page)

    context = {
        "wallet": wallet,
        "transactions": transactions,
        "selected_type": transaction_type,
    }

    return render(
        request,
        "wallet/wallet.html",
        context,
    )