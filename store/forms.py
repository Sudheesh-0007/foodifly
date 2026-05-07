# store/forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Removed 'image' from here since we use the custom gallery uploader now
        fields = ['name', 'slug', 'category', 'description', 'isActive'] 
        
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        
        # Apply CSS dynamically based on the input type
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                # Specific class for the toggle switch
                field.widget.attrs['class'] = 'form-check-input' 
            else:
                # Class for all other text/dropdown inputs
                field.widget.attrs['class'] = 'form-control custom-input'