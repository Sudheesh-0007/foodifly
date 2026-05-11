from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def custom_login_required(view_func):

    @wraps(view_func)

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:

            messages.warning(

                request,

                "Please login to continue"
            )

            return redirect('login')

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper