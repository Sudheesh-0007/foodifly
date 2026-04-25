from django import forms
from .models import Account,UserProfile
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : '. . . . . . . .  . .',
        'class' : 'custom-input'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : '. . . . . . . . . . . .'
    }))
    
    class Meta:
        model = Account
        field =  fields = ['first_name','last_name','phone_number','email','password']

    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password     = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        phone = self.cleaned_data.get('phone_number')
        first_name = self.cleaned_data.get('first_name')


        if password != confirm_password:
            raise forms.ValidationError("Password Does Not Match")
        try:
            validate_password(password)
        except ValidationError as e:
            self.add_error('password', e)

        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits")

        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be 10 digits")
        
        if phone and phone[0] not in ['6','7','8','9']:
            raise forms.ValidationError("Enter valid Phone number")
        
        if not first_name.isalpha():
            raise forms.ValidationError("First name should contain only letters")

        if len(first_name) < 3:
            raise forms.ValidationError("First name must be at least 3 characters")



    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = "Enter First Name"    
        self.fields['last_name'].widget.attrs['placeholder'] = "Enter Last Name"    
        self.fields['phone_number'].widget.attrs['placeholder'] = "  Enter Phone Number"    
        self.fields['email'].widget.attrs['placeholder'] = "Enter Email" 
        for field in self.fields :
            self.fields[field].widget.attrs['class'] = 'custom-input'


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        # Automatically apply your custom CSS class to all text inputs
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control custom-input'

class UserProfileForm(forms.ModelForm):
    # Hide the default ugly file input so we can trigger it with your custom buttons
    profile_image = forms.ImageField(required=False, error_messages={'invalid':("Image files only")}, widget=forms.FileInput(attrs={'class': 'd-none', 'id': 'profileImageInput'}))
    
    class Meta:
        model = UserProfile
        fields = ('profile_image',)
