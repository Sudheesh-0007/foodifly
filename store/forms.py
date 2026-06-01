from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = ["name", "slug", "category", "description", "isActive"]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            if isinstance(field.widget, forms.CheckboxInput):

                field.widget.attrs["class"] = "form-check-input"

            else:

                field.widget.attrs["class"] = "form-control custom-input"

    def validate_variants(
        self,
        variant_values,
        variant_prices,
        variant_stocks,
        variant_statuses,
    ):

        if not variant_values:

            raise forms.ValidationError("At least one variant is required.")

        values = [v.strip().lower() for v in variant_values]

        if len(values) != len(set(values)):

            raise forms.ValidationError("Duplicate variants are not allowed.")

        for value, price, stock in zip(
            variant_values,
            variant_prices,
            variant_stocks,
        ):

            if not value.strip():

                raise forms.ValidationError("Variant value cannot be empty.")

            try:

                if float(price) <= 0:

                    raise forms.ValidationError(
                        "Variant price must be greater than zero."
                    )

            except ValueError:

                raise forms.ValidationError("Invalid variant price.")

            try:

                if int(stock) < 0:

                    raise forms.ValidationError("Stock cannot be negative.")

            except ValueError:

                raise forms.ValidationError("Invalid stock value.")

        if not any(status == "True" for status in variant_statuses):

            raise forms.ValidationError("At least one variant must be active.")
