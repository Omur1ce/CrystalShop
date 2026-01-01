from decimal import Decimal
from typing import Dict

CART_SESSION_KEY = "cart"  # { "product_id": quantity }

def get_cart(session) -> Dict[str, int]:
    return session.get(CART_SESSION_KEY, {})

def save_cart(session, cart: Dict[str, int]) -> None:
    session[CART_SESSION_KEY] = cart
    session.modified = True

def add_to_cart(session, product_id: int, qty: int = 1) -> None:
    cart = get_cart(session)
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + qty
    if cart[pid] <= 0:
        cart.pop(pid, None)
    save_cart(session, cart)

def set_qty(session, product_id: int, qty: int) -> None:
    cart = get_cart(session)
    pid = str(product_id)
    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty
    save_cart(session, cart)

def clear_cart(session) -> None:
    save_cart(session, {})

def cart_count(session) -> int:
    cart = get_cart(session)
    return sum(cart.values())
