from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="products"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/clear/", views.cart_clear, name="cart_clear"),
    path("account/", views.account, name="account"),
    path("signup/", views.signup, name="signup")
]
