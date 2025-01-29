from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import ProfileUpdateView, profile_view

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('part/<int:part_id>/', views.part_detail, name='part_detail'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/logged_out'), name='logout'),
    path('logged_out/', views.logged_out, name='logged_out'),  # Add a view for the logged out page
    path('register/', views.register, name='register'),
    path('add_part/', views.add_part, name='add_part'),
    path('edit_part/<int:part_id>/', views.edit_part, name='edit_part'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:part_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart_quantity/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('orders/', views.order_history, name='order_history'),
    path('search/', views.search, name='search'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_summary/', views.order_summary, name='order_summary'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:part_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('profile/', profile_view, name='profile'),
    path('profile/create/', views.create_profile, name='create_profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('about/', views.about_us, name='about_us'),
]
