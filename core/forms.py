from django import forms
from .models import Part, Customer, Review, Category


# Form for creating and updating a part
class PartForm(forms.ModelForm):
    CURRENCY_CHOICES = [
        ('KES', 'KES'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
    ]
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, initial='KES')

    class Meta:
        model = Part
        fields = ['name', 'category', 'description', 'price', 'stock', 'image', 'currency']


# Form for handling search queries
class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)


# Form for updating the user's profile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']


# Form for creating and submitting a review
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


# Form for filtering parts based on category and price range
class FilterForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    min_price = forms.DecimalField(required=False, min_value=0, decimal_places=2, label='Min Price')
    max_price = forms.DecimalField(required=False, min_value=0, decimal_places=2, label='Max Price')

    # Custom validation for min_price and max_price
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        # Ensure min_price is not greater than max_price
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError("Minimum price cannot be greater than maximum price.")
        return cleaned_data


# Form for creating and updating categories
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
