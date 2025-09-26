from django.views import View
from django.views.generic import TemplateView, CreateView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import OrderForm, OrderItemForm
from .models import Order, OrderItem
from core.models import MenuItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

# --- Helpers for cart session ---
def get_cart(request):
    return request.session.get("cart", [])

def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True

# --- 1. Add to Cart ---
class CartAddView(View):
    form_class = OrderItemForm

    
    def post(self, request, *args, **kwargs):
        logger.debug(f"POST data: {request.POST}")
        form = self.form_class(request.POST)
        if form.is_valid():
            menu_item = form.cleaned_data['menu_item']
            quantity = form.cleaned_data['quantity']
            logger.info(f"Valid form: menu_item={menu_item.id}, quantity={quantity}")
            cart = get_cart(request)

            # Update or append item
            for item in cart:
                if item["menu_item_id"] == menu_item.id:
                    item_quantity = item.get("quantity", 0) or 0
                    new_quantity = quantity or 0
                    item["quantity"] = int(item_quantity) + int(new_quantity)
                    logger.debug(f"Updated existing item: {item}")
                    break
            else:
                cart.append({
                    "menu_item_id": menu_item.id,
                    "name": menu_item.name,
                    "price": str(menu_item.price),
                    "quantity": quantity,
                })
                logger.debug(f"Added new item: {menu_item.name}, quantity={quantity}")

            save_cart(request, cart)
            messages.success(request, f"{menu_item.name} added to cart!")
            return redirect("core:menu")
        else:
            logger.error(f"Form invalid: {form.errors.as_json()}")
            messages.error(request, f"Failed to add item to cart: {form.errors.as_text()}")
            return redirect("core:menu")


# --- 2. View Cart ---
class CartDetailView(TemplateView):
    template_name = "orders/cart_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        cart_total = sum(float(item["price"]) * item["quantity"] for item in cart)
        context.update({
            "cart": cart,
            "cart_total": cart_total,
            "order_form": OrderForm(initial={'user': self.request.user if self.request.user.is_authenticated else None}),
        })
        return context

@require_http_methods(["GET"])
def clear_cart(request):
    save_cart(request, [])
    messages.success(request, "Cart cleared.")
    return redirect("core:menu")

# --- 3. Checkout / Create Order ---
class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/checkout.html"
    success_url = reverse_lazy("payments:mpesa_initiate")  # Redirect to payment initiation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        cart_total = sum(float(item["price"]) * item["quantity"] for item in cart) if cart else 0
        context.update({
            'cart_total': cart_total,
            'phone_number': self.request.user.phone_no if self.request.user.is_authenticated else None,
        })
        return context

    def form_valid(self, form):
        cart = get_cart(self.request)
        logger.info(f"Valid form: cart={cart}")
        if not cart:
            messages.error(self.request, "Cart is empty.")
            return redirect("cart_detail")

        order = form.save(commit=False)
        if self.request.user.is_authenticated:
            order.user = self.request.user
            order.total_price = sum(float(item["price"]) * item["quantity"] for item in cart)
            order.status = 'pending'
            logger.debug(f"Valid form: user={self.request.user}, total_price={order.total_price}")
        order.save()

        # Create OrderItems
        for item in cart:
            menu_item = MenuItem.objects.get(id=item["menu_item_id"])
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item["quantity"],
                price=menu_item.price,
            )

        self.request.session['pending_order_id'] = order.id
        self.request.session['order_total'] = str(order.total_price)
        self.request.session['order_phone'] = self.request.user.phone_no
        logger.debug(f"Valid form: order_id={order.id}, total_price={order.total_price}")

        save_cart(self.request, [])  # Clear cart
        messages.success(self.request, "Order placed successfully!")
        return super().form_valid(form)

# --- 4. Order Success ---
class OrderSuccessView(TemplateView):
    template_name = "orders/order_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.session.get('pending_order_id')
        order = Order.objects.get(id=order_id) if order_id else None
        context['order'] = order
        return context

# --- 5. Cancel Order ---
class OrderCancelView(View):
    def get(self, request):
        order_id = request.session.get('pending_order_id')
        if order_id:
            order = Order.objects.get(id=order_id)
            order.status = 'cancelled'
            order.save()
            messages.success(request, "Order cancelled.")
            del request.session['pending_order_id']
        return redirect("core:menu")