from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import Account
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_login(request):
    # Change is_superuser to is_admin
    if request.user.is_authenticated:
        if request.user.is_admin: # Changed here
            return redirect('admin_user_management')
        else:
            auth.logout(request)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(email=email, password=password)

        # Change is_superuser to is_admin
        if user is not None and user.is_admin: # Changed here
            auth.login(request, user)
            return redirect('admin_user_management')
        else:
            messages.error(request, 'Admin access only.')
            return redirect('admin_login')
            
    return render(request, 'admin_panel/admin_login.html')


@login_required(login_url='admin_login')
def admin_user_management(request):
    # 1. Fetch all users, sorted by latest joined first
    users_list = Account.objects.all().order_by('-date_joined')

    # 2. Search logic
    query = request.GET.get('keyword')
    if query:
        users_list = users_list.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(email__icontains=query)
        )

    # 3. Pagination (10 users per page)
    paginator = Paginator(users_list, 10)
    page = request.GET.get('page')
    
    # Use get_page; it handles PageNotAnInteger and EmptyPage automatically!
    paged_users = paginator.get_page(page)

    context = {
        'users': paged_users,  # We pass paged_users but NAME it 'users' for the HTML
        'keyword': query,
        'total_count': Account.objects.count(), # For the white stats card
        'active_count': Account.objects.filter(is_active=True).count(), # For the green stats card
    }
    return render(request, 'admin_panel/user_manage.html', context)

# i. Block/Unblock Logic [cite: 3535, 4761]
def toggle_user_status(request, user_id):
    # Fetch the specific user
    user = get_object_or_404(Account, id=user_id)
    
    if user.is_active:
        user.is_active = False
        messages.success(request, f'User {user.email} has been blocked.')
    else:
        user.is_active = True
        messages.success(request, f'User {user.email} has been unblocked.')
    
    user.save()
    return redirect('admin_user_management')
def admin_logout(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out of the Sovereign Management Portal.')
    return redirect('admin_login')