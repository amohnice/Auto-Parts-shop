from django import forms
from .models import Part, Customer, Review, Category

class PartForm(forms.ModelForm):
    currency = forms.CharField(max_length=3, initial='USD')

    class Meta:
        model = Part
        fields = ['name', 'category', 'description', 'price', 'stock', 'image', 'currency']

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class FilterForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    min_price = forms.DecimalField(required=False, min_value=0, decimal_places=2)
    max_price = forms.DecimalField(required=False, min_value=0, decimal_places=2)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']