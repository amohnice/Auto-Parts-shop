from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

# Category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name

# Part model
class Part(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='parts/', null=True, blank=True)
    currency = models.CharField(max_length=3, default='KES')

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.stock < 5


# Customer model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Make user field nullable temporarily
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

# Order model
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    parts = models.ManyToManyField(Part)
    date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return "Order {} - {}".format(self.id, self.customer)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart for {}".format(self.user.username)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return "{} x {}".format(self.quantity, self.part.name)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_request_id = models.CharField(max_length=100, unique=True)
    transaction_code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {} - {}".format(self.user.username, self.amount, self.status)

class Review(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {} stars".format(self.user.username, self.rating)

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # Discount as a percentage
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField()

    def __str__(self):
        return self.code

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.part.name)
