from django.views import View
from django.views.generic import TemplateView, CreateView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import OrderForm, OrderItemForm
from .models import Order, OrderItem
from core.models import MenuItem

# --- Helpers for cart session ---
def get_cart(request):
    return request.session.get("cart", [])

def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True

# --- 1. Add to Cart ---
class CartAddView(View):
    model = OrderItem
    form_class= OrderItemForm
    
    def post(self, request, *args, **kwargs):
        form = OrderItemForm(request.POST)
        if form.is_valid():
            menu_item = form.cleaned_data['menu_item']
            quantity = form.cleaned_data['quantity']
            cart = get_cart(request)

            # Update or append item
            for item in cart:
                if item["menu_item_id"] == menu_item.id:
                    item["quantity"] += quantity
                    break
            else:
                cart.append({
                    "menu_item_id": menu_item.id,
                    "name": menu_item.name,
                    "price": str(menu_item.price),
                    "quantity": quantity,
                })

            save_cart(request, cart)
            messages.success(request, f"{menu_item.name} added to cart!")
            return redirect("core:menu") 
        else:
            #messages.error(request, "Invalid item or quantity.")
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

# --- 3. Checkout / Create Order ---
class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/checkout.html"
    success_url = reverse_lazy("order_success")

    def form_valid(self, form):
        cart = get_cart(self.request)
        if not cart:
            messages.error(self.request, "Cart is empty.")
            return redirect("cart_detail")

        order = form.save(commit=False)
        if self.request.user.is_authenticated:
            order.user = self.request.user
        order.save()

        # Create OrderItems (signals will handle total_price)
        for item in cart:
            menu_item = MenuItem.objects.get(id=item["menu_item_id"])
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item["quantity"],
                price=menu_item.price,
            )

        save_cart(self.request, [])  # Clear cart
        messages.success(self.request, "Order placed successfully!")
        return super().form_valid(form)

# --- 4. Order Success ---
class OrderSuccessView(TemplateView):
    template_name = "orders/order_success.html"