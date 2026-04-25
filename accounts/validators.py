from django.core.exceptions import ValidationError

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