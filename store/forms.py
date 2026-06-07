from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'John Doe'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'john@example.com'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '+1 234 567 890'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': '123 Main St, Apt 4B',
            'rows': 3
        })
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'New York'})
    )
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '10001'})
    )
