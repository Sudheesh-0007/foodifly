from django.core.exceptions import ValidationError
import re


class AlphanumericPasswordValidator:

    def validate(self, password, user=None):

        if not any(char.isalpha() for char in password):

            raise ValidationError(
                "Your password must contain at least one letter.",
                code='password_no_letters',
            )

        if not any(char.isdigit() for char in password):

            raise ValidationError(
                "Your password must contain at least one number.",
                code='password_no_number',
            )

    def get_help_text(self):

        return "Your password must contain a mix of letters and numbers."


def validate_phone(value):

    if not re.fullmatch(r'^[6-9]\d{9}$', value):

        raise ValidationError(
            "Enter a valid 10-digit phone number."
        )


def validate_postal_code(value):

    if not re.fullmatch(r'^\d{6}$', value):

        raise ValidationError(
            "Postal code must be 6 digits."
        )


def validate_name(value):

    if not value.replace(" ", "").isalpha():

        raise ValidationError(
            "This field should contain only letters."
        )