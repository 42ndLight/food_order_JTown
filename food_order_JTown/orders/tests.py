from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser
from core.models import Category, MenuItem
from orders.models import Order, OrderItem
from decimal import Decimal

class OrderCheckoutFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = CustomUser.objects.create_user(
            username='254712345678',
            phone_no='254712345678',
            role='customer'
        )
        self.category = Category.objects.create(name='Burgers', description='Delicious burgers')
        self.menu_item = MenuItem.objects.create(
            name='Classic Burger',
            price=Decimal('500.00'),
            category_id=self.category,
            available=True
        )

    def test_cart_detail_get_shows_items_only(self):
        # Set cart in session
        session = self.client.session
        session['cart'] = [{
            'menu_item_id': self.menu_item.id,
            'name': self.menu_item.name,
            'price': str(self.menu_item.price),
            'quantity': 2,
        }]
        session.save()

        response = self.client.get(reverse('orders:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/cart_detail.html')
        self.assertContains(response, 'Classic Burger')
        self.assertContains(response, 'KES 1000.00')
        self.assertContains(response, reverse('orders:order_create'))
        # Should NOT contain delivery picker form inputs on cart
        self.assertNotContains(response, 'id="use-current-location"')

    def test_checkout_requires_login(self):
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('users:customer_send_otp')))

    def test_checkout_get_authenticated(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/checkout.html')
        self.assertContains(response, '254712345678')
        self.assertContains(response, 'id="use-current-location"')
        self.assertContains(response, 'name="building_name"')
        self.assertContains(response, 'name="address"')

    def test_checkout_post_creates_order_without_session_delivery_info(self):
        self.client.force_login(self.customer)

        # Set cart in session WITHOUT any delivery_info in session
        session = self.client.session
        session['cart'] = [{
            'menu_item_id': self.menu_item.id,
            'name': self.menu_item.name,
            'price': str(self.menu_item.price),
            'quantity': 2,
        }]
        if 'delivery_info' in session:
            del session['delivery_info']
        session.save()

        post_data = {
            'user': self.customer.id,
            'building_name': 'Green Tower',
            'street': 'Moi Avenue',
            'address': 'Floor 3, Apt 12',
            'latitude': '-1.286389',
            'longitude': '36.817223',
            'delivery_fee': '50.00',
        }

        response = self.client.post(reverse('orders:order_create'), post_data)
        self.assertRedirects(response, reverse('payments:mpesa-push'), fetch_redirect_response=False)

        # Check Order was created in DB
        order = Order.objects.get(user=self.customer)
        self.assertEqual(order.building_name, 'Green Tower')
        self.assertEqual(order.delivery_fee, Decimal('50.00'))
        self.assertEqual(order.total_price, Decimal('1050.00'))  # 500*2 + 50
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)

        # Check session has keys needed by payments view
        session = self.client.session
        self.assertEqual(session.get('pending_order_id'), order.id)
        self.assertEqual(session.get('order_total'), '1050.00')
        self.assertEqual(session.get('order_phone'), '254712345678')

        # Cart should be cleared
        self.assertEqual(session.get('cart'), [])
