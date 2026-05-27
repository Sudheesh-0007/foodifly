from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_required(view_func):

    @login_required(login_url='admin_login')

    def wrapper(request, *args, **kwargs):

        if not request.user.is_admin:

            messages.error(
                request,
                "You are not authorized to access admin panel."
            )

            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper