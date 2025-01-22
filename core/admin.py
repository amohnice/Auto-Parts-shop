from django.contrib import admin
from .models import Category, Part, Customer, Order

class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'currency')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    fields = ['name', 'category', 'description', 'price', 'stock', 'image', 'currency']

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')
    search_fields = ('first_name', 'last_name', 'email')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date', 'completed')
    search_fields = ('customer__first_name', 'customer__last_name')
    list_filter = ('completed',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')
    search_fields = ('name',)

# Register your models with custom admin classes
admin.site.register(Category, CategoryAdmin)  # Corrected this line
admin.site.register(Part, PartAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)

# admin interface http://127.0.0.1:8000/admin/ , username; admin , password; admin123
