from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Account, Address, UserProfile
from .validators import validate_name, validate_phone, validate_postal_code


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": ". . . . . . . .  . .", "class": "custom-input"}
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": ". . . . . . . . . . . ."})
    )
    referral_code = forms.CharField(max_length=10,required=False,)

    class Meta:
        model = Account
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "password",
        ]

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        phone = self.cleaned_data.get("phone_number")
        first_name = self.cleaned_data.get("first_name")

        if password != confirm_password:
            raise forms.ValidationError("Password Does Not Match")
        try:
            validate_password(password)
        except ValidationError as e:
            self.add_error("password", e)

        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits")

        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be 10 digits")

        if phone and phone[0] not in ["6", "7", "8", "9"]:
            raise forms.ValidationError("Enter valid Phone number")

        if not first_name.isalpha():
            raise forms.ValidationError("First name should contain only letters")

        if len(first_name) < 3:
            raise forms.ValidationError("First name must be at least 3 characters")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter First Name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter Last Name"
        self.fields["phone_number"].widget.attrs["placeholder"] = "  Enter Phone Number"
        self.fields["email"].widget.attrs["placeholder"] = "Enter Email"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "custom-input"


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("first_name", "last_name", "phone_number")

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        phone = cleaned_data.get("phone_number")

        if first_name:
            if not first_name.isalpha():
                self.add_error("first_name", "Only letters allowed")

            if len(first_name) < 3:
                self.add_error("first_name", "Minimum 3 characters required")

        if phone:
            if not phone.isdigit():
                self.add_error("phone_number", "Only digits allowed")

            if len(phone) != 10:
                self.add_error("phone_number", "Must be 10 digits")

            if phone[0] not in ["6", "7", "8", "9"]:
                self.add_error("phone_number", "Enter valid phone number")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control custom-input"


class UserProfileForm(forms.ModelForm):

    profile_image = forms.ImageField(
        required=False,
        error_messages={"invalid": ("Image files only")},
        widget=forms.FileInput(attrs={"class": "d-none", "id": "profileImageInput"}),
    )

    class Meta:
        model = UserProfile
        fields = ("profile_image",)


class AddressForm(forms.ModelForm):

    first_name = forms.CharField(validators=[validate_name])

    last_name = forms.CharField(validators=[validate_name])

    city = forms.CharField(validators=[validate_name])

    district = forms.CharField(validators=[validate_name])

    state = forms.CharField(validators=[validate_name])

    phone = forms.CharField(validators=[validate_phone])

    postal_code = forms.CharField(validators=[validate_postal_code])

    class Meta:

        model = Address

        fields = [
            "first_name",
            "last_name",
            "address_line_1",
            "phone",
            "city",
            "postal_code",
            "district",
            "state",
            "country",
            "is_default",
        ]
