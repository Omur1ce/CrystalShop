from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
import stripe
from django.conf import settings


from .models import Product
from .cart import add_to_cart, cart_count, clear_cart, get_cart, set_qty


def product_list(request: HttpRequest) -> HttpResponse:
    q = (request.GET.get("q") or "").strip()
    products = Product.objects.all().order_by("name")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    return render(request, "store/products.html", {
        "products": products,
        "q": q,
        "cart_count": cart_count(request.session),
    })


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
    # ✅ Force login before adding to cart
    if not request.user.is_authenticated:
        # Redirect to login and then back to the page they were on
        return redirect_to_login(next=request.get_full_path())

    get_object_or_404(Product, id=product_id)  # validate product exists
    add_to_cart(request.session, product_id, qty=1)
    return redirect(request.META.get("HTTP_REFERER", "products"))


def cart_view(request: HttpRequest) -> HttpResponse:
    cart = get_cart(request.session)  # {"id": qty}

    ids = [int(pid) for pid in cart.keys()]
    products_by_id = Product.objects.in_bulk(ids)

    # prune invalid ids (if any)
    changed = False
    for pid_str in list(cart.keys()):
        if int(pid_str) not in products_by_id:
            cart.pop(pid_str, None)
            changed = True
    if changed:
        request.session["cart"] = cart
        request.session.modified = True

    items = []
    total = Decimal("0.00")

    for pid_str, qty in cart.items():
        p = products_by_id[int(pid_str)]
        line_total = p.price_gbp * qty
        total += line_total
        items.append({"product": p, "qty": qty, "line_total": line_total})

    return render(request, "store/cart.html", {
        "items": items,
        "total": total,
        "cart_count": cart_count(request.session),
    })


@require_POST
@login_required
def cart_update(request: HttpRequest, product_id: int) -> HttpResponse:
    qty = int(request.POST.get("qty", "1"))
    set_qty(request.session, product_id, qty)
    return redirect("cart")


@require_POST
@login_required
def cart_clear(request: HttpRequest) -> HttpResponse:
    clear_cart(request.session)
    return redirect("cart")


@login_required
def account(request: HttpRequest) -> HttpResponse:
    return render(request, "store/account.html", {
        "cart_count": cart_count(request.session),
    })

def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after signup
            return redirect("account")
    else:
        form = UserCreationForm()

    return render(request, "store/signup.html", {
        "form": form,
        "cart_count": cart_count(request.session),
    })

@login_required
def checkout_page(request: HttpRequest) -> HttpResponse:
    # Just a confirmation page that shows cart summary and a "Pay" button
    cart = get_cart(request.session)
    ids = [int(pid) for pid in cart.keys()]
    products_by_id = Product.objects.in_bulk(ids)

    items = []
    total = Decimal("0.00")
    for pid_str, qty in cart.items():
        p = products_by_id.get(int(pid_str))
        if not p:
            continue
        line_total = p.price_gbp * qty
        total += line_total
        items.append({"product": p, "qty": qty, "line_total": line_total})

    return render(request, "store/checkout.html", {
        "items": items,
        "total": total,
        "cart_count": cart_count(request.session),
    })


@require_POST
@login_required
def create_checkout_session(request: HttpRequest) -> HttpResponse:
    stripe.api_key = settings.STRIPE_SECRET_KEY

    cart = get_cart(request.session)
    ids = [int(pid) for pid in cart.keys()]
    products_by_id = Product.objects.in_bulk(ids)

    # Build Stripe line items
    line_items = []
    for pid_str, qty in cart.items():
        p = products_by_id.get(int(pid_str))
        if not p:
            continue

        # Stripe expects amount in pennies
        unit_amount = int((p.price_gbp * 100).quantize(Decimal("1")))
        line_items.append({
            "price_data": {
                "currency": settings.STRIPE_CURRENCY,
                "product_data": {"name": p.name},
                "unit_amount": unit_amount,
            },
            "quantity": qty,
        })

    if not line_items:
        return redirect("cart")

    domain = request.build_absolute_uri("/")[:-1]  # http://127.0.0.1:8000
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=f"{domain}/checkout/success/",
        cancel_url=f"{domain}/checkout/cancel/",
    )

    return redirect(session.url, code=303)


@login_required
def checkout_success(request: HttpRequest) -> HttpResponse:
    # For now: clear cart on success page visit (dev-friendly)
    clear_cart(request.session)
    return render(request, "store/checkout_success.html", {
        "cart_count": cart_count(request.session),
    })


@login_required
def checkout_cancel(request: HttpRequest) -> HttpResponse:
    return render(request, "store/checkout_cancel.html", {
        "cart_count": cart_count(request.session),
    })

