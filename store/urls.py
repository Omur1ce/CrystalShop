from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="products"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/clear/", views.cart_clear, name="cart_clear"),
    path("account/", views.account, name="account"),
    path("signup/", views.signup, name="signup"),
    path("checkout/", views.checkout_page, name="checkout"),
    path("checkout/create-session/", views.create_checkout_session, name="create_checkout_session"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),
]
