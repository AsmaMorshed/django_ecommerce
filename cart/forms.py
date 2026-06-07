from django import forms

QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 11)]


class AddToCartForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=QUANTITY_CHOICES,
        coerce=int,
        initial=1,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    color    = forms.CharField(required=False, widget=forms.HiddenInput)
    size     = forms.CharField(required=False, widget=forms.HiddenInput)
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )


class CheckoutForm(forms.Form):
    # ---- Personal Info ----
    first_name   = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name    = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email        = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone        = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )

    # ---- Delivery Address ----
    address      = forms.CharField(
        max_length=250,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'})
    )
    city         = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    postal_code  = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal / ZIP Code'})
    )
    country      = forms.CharField(
        max_length=100,
        initial='Bangladesh',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'})
    )
