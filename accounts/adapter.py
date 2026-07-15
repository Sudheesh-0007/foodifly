from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import uuid
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        email = data.get("email", "")

        username = email.split("@")[0]

        if not username:
            username = f"user_{uuid.uuid4().hex[:8]}"

        original = username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{original}{counter}"
            counter += 1

        user.username = username

        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # Google accounts are already verified by Google
        user.is_active = True
        user.save()

        return user
    