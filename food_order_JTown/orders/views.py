from django.views import View
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import OrderForm, OrderItemForm
from .models import Order, OrderItem
from core.models import MenuItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from decimal import Decimal
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

            if request.headers.get('HX-Request'):
                # Calculate new count for the partial
                count = sum(item.get('quantity', 0) for item in cart)
                return render(request, "components/cart_badge_partial.html", {'cart_count': count})

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
        })
        return context

@require_http_methods(["GET"])
def clear_cart(request):
    save_cart(request, [])
    messages.success(request, "Cart cleared.")
    return redirect("core:menu")

# --- 3. Checkout / Create Order ---
class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/checkout.html"
    login_url = reverse_lazy('users:customer_send_otp')
    success_url = reverse_lazy("payments:mpesa-push")

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial['user'] = self.request.user
        initial['delivery_fee'] = Decimal('0.00')
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        cart_subtotal = sum(float(item["price"]) * item["quantity"] for item in cart) if cart else 0
        delivery_fee = 0.00
        
        context.update({
            'order_form': context.get('form'),
            'cart_subtotal': cart_subtotal,
            'delivery_fee': delivery_fee,
            'grand_total': cart_subtotal + delivery_fee,
            'phone_number': self.request.user.phone_no if self.request.user.is_authenticated else None,
        })
        return context

    def form_invalid(self, form):
        logger.error(f"Order form invalid: {form.errors.as_json()}")
        messages.error(self.request, "Please check the delivery details and try again.")
        return super().form_invalid(form)

    def form_valid(self, form):
        cart = get_cart(self.request)
        if not cart:
            messages.error(self.request, "Cart is empty.")
            return redirect("orders:cart_detail")

        order = form.save(commit=False)
        
        # Capture location fields from form / POST
        order.address = form.cleaned_data.get('address') or self.request.POST.get('address', order.address)
        order.building_name = form.cleaned_data.get('building_name') or self.request.POST.get('building_name', order.building_name)
        order.street = form.cleaned_data.get('street') or self.request.POST.get('street', order.street)
        
        raw_lat = form.cleaned_data.get('latitude') or self.request.POST.get('latitude')
        raw_lng = form.cleaned_data.get('longitude') or self.request.POST.get('longitude')
        raw_fee = form.cleaned_data.get('delivery_fee') or self.request.POST.get('delivery_fee')

        if raw_lat:
            try:
                order.latitude = Decimal(str(raw_lat))
            except (ValueError, TypeError, ArithmeticError):
                pass
        if raw_lng:
            try:
                order.longitude = Decimal(str(raw_lng))
            except (ValueError, TypeError, ArithmeticError):
                pass
        if raw_fee:
            try:
                order.delivery_fee = Decimal(str(raw_fee))
            except (ValueError, TypeError, ArithmeticError):
                order.delivery_fee = Decimal('0.00')
        else:
            order.delivery_fee = Decimal('0.00')

        if self.request.user.is_authenticated:
            order.user = self.request.user
            
        cart_subtotal = sum(Decimal(str(item["price"])) * item["quantity"] for item in cart)
        order.total_price = cart_subtotal + order.delivery_fee
        order.status = 'pending'
        
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
        
        # Clear cart
        save_cart(self.request, [])
        if 'delivery_info' in self.request.session:
            del self.request.session['delivery_info']
            
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