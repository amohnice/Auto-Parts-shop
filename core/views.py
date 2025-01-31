from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Part, Cart, CartItem, Order, Customer, Transaction, Review, Coupon, Wishlist
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from .forms import PartForm, SearchForm, UserProfileForm, ReviewForm, FilterForm
from django_daraja.mpesa.core import MpesaClient
from django.http import JsonResponse, HttpResponse
import json, logging
logger = logging.getLogger(__name__)
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages

def index(request):
    categories = Category.objects.all()
    return render(request, 'core/index.html', {'categories': categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    parts = Part.objects.filter(category=category)
    return render(request, 'core/category_detail.html', {'category': category, 'parts': parts})

def part_detail(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    reviews = Review.objects.filter(part=part)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.part = part
            review.save()
            return redirect('part_detail', part_id=part.id)
    else:
        form = ReviewForm()
    return render(request, 'core/part_detail.html', {'part': part, 'reviews': reviews, 'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user, first_name='', last_name='', email=user.email, phone_number='', address='')
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def add_part(request):
    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES)
        if form.is_valid():
            part = form.save(commit=False)
            part.currency = form.cleaned_data['currency']
            part.save()
            return redirect('index')
    else:
        form = PartForm()
    return render(request, 'core/add_part.html', {'form': form})

def edit_part(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES, instance=part)
        if form.is_valid():
            part.currency = form.cleaned_data['currency']
            part.save()
            return redirect('part_detail', part_id=part.id)
    else:
        form = PartForm(instance=part)
    return render(request, 'core/edit_part.html', {'form': form})

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    return render(request, 'core/view_cart.html', {'items': items})

@login_required
def add_to_cart(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, part=part)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')

def update_cart_quantity(request, item_id):
    try:
        # Get the new quantity from the GET request
        quantity = int(request.GET.get('quantity'))

        # Update the cart item in the database
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)  # Use cart__user to filter by user
        cart_item.quantity = quantity  # Use the `quantity` variable here
        cart_item.save()

        # Recalculate the total price for the cart
        cart_items = CartItem.objects.filter(cart__user=request.user)  # Filter by cart's user
        total_price = sum(item.quantity * item.part.price for item in cart_items)
        subtotal = sum(item.quantity * item.part.price for item in cart_items)

        # Return the updated totals
        return JsonResponse({'success': True, 'total_price': total_price, 'subtotal': subtotal})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cart item not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def order_history(request):
    customer = get_object_or_404(Customer, user=request.user)
    orders = Order.objects.filter(customer=customer)
    return render(request, 'core/order_history.html', {'orders': orders})
def search(request):
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    form = SearchForm(request.GET)
    filter_form = FilterForm(request.GET)

    results = Part.objects.all()

    if query:
        results = results.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        results = results.filter(category__id=category)
    if min_price:
        results = results.filter(price__gte=min_price)
    if max_price:
        results = results.filter(price__lte=max_price)

    return render(request, 'core/search.html', {'form': form, 'filter_form': filter_form, 'results': results})

def checkout(request):
    logger.info("MPESA_ENVIRONMENT: {os.environ.get('DARAJA_ENVIRONMENT')}")
    logger.info("CONSUMER_KEY: {os.environ.get('DARAJA_CONSUMER_KEY')}")

    # Ensure the cart is fetched correctly
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Access cart items through the 'items' related name
    total = sum(item.part.price * item.quantity for item in cart.items.all())
    total = int(total)  # Convert to integer for Mpesa amount

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        # amount = request.POST.get('amount')
        # amount = int(float(amount))  # Uncomment if you want to accept dynamic amount

        account_reference = 'Order Payment'
        transaction_desc = 'Payment for order'
        callback_url = 'https://yourdomain.com/mpesa/callback/'

        mpesa_client = MpesaClient()  # Assuming you've defined this client somewhere
        response = mpesa_client.stk_push(
            phone_number=phone_number,
            amount=total,
            account_reference=account_reference,
            transaction_desc=transaction_desc,
            callback_url=callback_url
        )

        # Create a transaction record
        transaction = Transaction.objects.create(
            user=request.user,
            phone_number=phone_number,
            amount=total,
            checkout_request_id=response.checkout_request_id,
            status='PENDING'
        )

        # Send order confirmation email (assuming the function is defined)
        send_order_confirmation(request.user)

        # Return a JSON response with the transaction ID
        return JsonResponse({'status': 'success', 'transaction_id': transaction.id})

    # Render the checkout page
    return render(request, 'core/checkout.html', {'cart_items': cart.items.all(), 'total': total})


@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')

        transaction = Transaction.objects.get(checkout_request_id=checkout_request_id)
        if result_code == 0:
            transaction.status = 'COMPLETED'
            transaction.transaction_code = stk_callback.get('CallbackMetadata')['Item'][1]['Value']
        else:
            transaction.status = 'FAILED'

        transaction.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})

@login_required
def order_summary(request):
    cart = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    subtotal = sum(item.quantity * item.part.price for item in items)
    total = subtotal
    return render(request, 'core/order_summary.html', {'items': items, 'subtotal': subtotal, 'total': total, 'currency': 'KSH'})

def send_order_confirmation(user):
    subject = 'Order Confirmation'
    message = 'Thank you for your order, {user.username}!\n\nYour order has been successfully placed and is being processed. Transaction ID: {transaction.transaction_code}\nAmount: {transaction.amount} KES'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)

@login_required
def profile(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        # Redirect to a profile creation page or create a Customer instance here
        return redirect('create_profile')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=customer)

    return render(request, 'core/profile.html', {'form': form})


@login_required
def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            return redirect('profile')
    else:
        form = UserProfileForm()

    return render(request, 'core/create_profile.html', {'form': form})

class ProfileUpdateView(UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'core/profile.html'

    def get_success_url(self):
        return reverse('profile')


@login_required
def profile_view(request):
    return render(request, 'core/profile.html', {'user': request.user})


@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            coupon = Coupon.objects.get(code=code, active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
            request.session['coupon_id'] = coupon.id
            return redirect('checkout')
        except Coupon.DoesNotExist:
            return render(request, 'core/apply_coupon.html', {'error': 'Invalid coupon code'})
    return render(request, 'core/apply_coupon.html')

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'core/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, part=part)

    if created:
        messages.success(request, 'Part added to wishlist.')
    else:
        messages.info(request, 'Part is already in your wishlist.')

    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id)

    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, 'Part removed from wishlist.')
    else:
        messages.error(request, 'Part not found in wishlist.')

    return redirect('wishlist')

# Autocomplete View
def autocomplete(request):
    if 'term' in request.GET:
        query = request.GET.get('term')
        qs = Part.objects.filter(name__icontains=query)[:10]  # Get matching parts

        # Return matching parts as a list of dictionaries with 'label' and 'value'
        results = [{'label': part.name, 'value': part.name} for part in qs]

        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)

def about_us(request):
    return render(request, 'core/about_us.html')

def logged_out(request):
    return render(request, 'core/logged_out.html')


# Test environment
import os

def test_environment(request):
    # Print environment variables
    print("MPESA Environment:", os.getenv('DARAJA_ENVIRONMENT'))
    print("Consumer Key:", os.getenv('DARAJA_CONSUMER_KEY'))
    return HttpResponse("Environment variables printed to the console.")
