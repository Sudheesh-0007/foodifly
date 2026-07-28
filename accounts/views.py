from allauth.socialaccount.signals import pre_social_login
from django.contrib import auth, messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.cache import never_cache

from .forms import AddressForm, RegistrationForm, UserForm, UserProfileForm
from .models import Account, Address, UserProfile,Referral


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            referral_code = form.cleaned_data.get("referral_code", "").strip().upper()
            referred_by = None
            if referral_code:
                try:
                    referred_by = Account.objects.get(
                        referral_code=referral_code
                    )

                except Account.DoesNotExist:
                    form.add_error("referral_code", "Invalid referral code.")
                    return render(request, "accounts/register.html", {"form": form})
            
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.phone_number = phone_number
            user.referred_by = referred_by
            user.save()
            if referred_by and referred_by.email.lower() == email.lower():
                messages.error(request, "You cannot use your own referral code.")
                return redirect("register")
            if referred_by:
                Referral.objects.create(
                    referrer=referred_by,
                    referred_user=user,
                )

            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string(
                "accounts/account_varification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(
                request,
                "Thank you for registering with us . we have sent you a varification email to your email address",
            )
            return redirect("login")

    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
@never_cache
def logout(request):
    auth.logout(request)
    messages.success(request, "You are Logged Out")

    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations ! Your account is activated.")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("register")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request, "Password reset email has been send to your email address."
            )
            return redirect("login")

        else:
            messages.error(request, "Account does not exist")
            return redirect("forgotPassword")

    return render(request, "accounts/forgotPassword.html")


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "please reset your password")
        return redirect("resetPassword")
    else:
        messages.error(request, "this link has been expired")
        return redirect("login")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password == confirm_password:
            uid = request.session.get("uid")
            try:
                user = Account.objects.get(pk=uid)
            except Account.DoesNotExist:
                messages.error(request, "Invalid user session")
                return redirect("login")
            try:
                validate_password(password, user=user)
            except ValidationError as e:
                messages.error(request, e)
                return redirect("resetPassword")

            user.set_password(password)
            user.save()
            if "uid" in request.session:
                del request.session["uid"]

            messages.success(request, "Passwors reset is successful")
            return redirect("login")

        else:
            messages.error(request, "password do not match!")
            return redirect("resetPassword")
    else:
        return render(request, "accounts/resetPassword.html")


@receiver(pre_social_login)
def activate_user_from_social(sender, request, sociallogin, **kwargs):

    user = sociallogin.user

    if user and user.id and not user.is_active:
        user.is_active = True
        user.save()
    
from orders.models import Order,OrderItem
from django.db.models import Sum
@login_required(login_url="login")
@never_cache
def user_dashboard(request):

    default_address = Address.objects.filter(user=request.user, is_default=True).first()

    context = {
        "default_address": default_address,
    }
    return render(request, "accounts/user_dashboard.html", context)


@login_required(login_url="login")
@never_cache
def account_settings(request):
    return render(request, "accounts/account_settings.html")


@login_required(login_url="login")
@never_cache
def edit_email(request):
    if request.method == "POST":

        if "new_email" in request.POST:
            new_email = request.POST.get("new_email")

            if new_email == request.user.email:
                messages.info(request, "This is already your current email address.")
                return redirect("edit_email")

            if Account.objects.filter(email=new_email).exists():
                messages.error(
                    request, "This email address is already in use by another account."
                )
                return redirect("edit_email")

            user = request.user
            current_site = get_current_site(request)
            mail_subject = "Verify your new email address"

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            encoded_email = urlsafe_base64_encode(force_bytes(new_email))

            message = render_to_string(
                "accounts/update_email_verification.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": uid,
                    "token": token,
                    "encoded_email": encoded_email,
                },
            )

            send_email = EmailMessage(mail_subject, message, to=[new_email])
            send_email.send()

            messages.success(
                request,
                "A verification link has been sent to your new email address. Please click it to complete the update.",
            )
            return redirect("edit_email")

        elif "old_password" in request.POST:
            old_password = request.POST.get("old_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if not request.user.check_password(old_password):
                messages.error(request, "Your old password was entered incorrectly.")
                return redirect("edit_email")

            if new_password != confirm_password:
                messages.error(request, "Your new passwords do not match.")
                return redirect("edit_email")

            if old_password == new_password:
                messages.error(
                    request,
                    "Your new password must be different from your current one.",
                )
                return redirect("edit_email")

            try:

                validate_password(new_password, request.user)
            except ValidationError as e:

                for error in e.messages:
                    messages.error(request, error)
                return redirect("edit_email")

            user = request.user
            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            messages.success(request, "Your password has been successfully updated.")
            return redirect("edit_email")

    return render(request, "accounts/edit_email.html")


def update_email_validate(request, uidb64, token, encoded_email):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
        new_email = urlsafe_base64_decode(encoded_email).decode()
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        if Account.objects.filter(email=new_email).exists():
            messages.error(
                request, "This email address was recently taken by another account."
            )
            return redirect("account_settings")

        user.email = new_email
        user.username = new_email.split("@")[0]
        user.save()
        logout(request)
        messages.success(request, "Your email address has been successfully updated!")
        return redirect("login")
    else:
        messages.error(
            request, "The email verification link is invalid or has expired."
        )
        return redirect("account_settings")


login_required(login_url="login")


def edit_profile(request):
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been successfully updated.")
            return redirect("edit_profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
        

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "userprofile": userprofile,
    }
    return render(request, "accounts/edit_profile.html", context)


@login_required(login_url="login")
def manage_addresses(request):

    addresses = Address.objects.filter(user=request.user).order_by(
        "-is_default", "-id"
    )[:3]

    context = {
        "addresses": addresses,
    }
    return render(request, "accounts/manage_addresses.html", context)


@login_required(login_url="login")
def add_address(request):

    if request.method == "POST":

        form = AddressForm(request.POST)

        if form.is_valid():

            address = form.save(commit=False)

            address.user = request.user

            is_default = form.cleaned_data.get("is_default")

            if not Address.objects.filter(user=request.user).exists():

                is_default = True

            if is_default:

                Address.objects.filter(user=request.user, is_default=True).update(
                    is_default=False
                )

            address.is_default = is_default

            address.save()

            messages.success(request, "New delivery address added successfully!")

            next_page = request.GET.get("next")

            if next_page == "checkout":

                return redirect("checkout")

            return redirect("address")


    else:

        form = AddressForm()

    context = {
        "form": form,
    }

    return render(request, "accounts/add_address.html", context)


@login_required(login_url="login")
def edit_address(request, id):

    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == "POST":

        form = AddressForm(request.POST, instance=address)

        if form.is_valid():

            address = form.save(commit=False)

            is_default = form.cleaned_data.get("is_default")

            if is_default:

                Address.objects.filter(user=request.user, is_default=True).exclude(
                    id=address.id
                ).update(is_default=False)

            address.is_default = is_default

            address.save()

            messages.success(request, "Delivery address updated successfully!")

            next_page = request.POST.get("next")

            if next_page == "checkout":
                return redirect("checkout")
            return redirect("address")


    else:
        form = AddressForm(instance=address)

    context = {
        "form": form,
        "address": address,
    }

    return render(request, "accounts/edit_address.html", context)


@login_required(login_url="login")
def delete_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)

    address.delete()

    messages.success(request, "Delivery address deleted successfully.")
    return redirect("address")
