from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser
from orders.models import Order
from payments.models import MpesaTransaction
from decimal import Decimal

class MpesaPaymentFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = CustomUser.objects.create_user(
            username='254712345678',
            phone_no='254712345678',
            role='customer'
        )
        self.order = Order.objects.create(
            user=self.customer,
            total_price=Decimal('1050.00'),
            building_name='Green Tower',
            status='pending'
        )

    def test_payment_push_requires_login(self):
        response = self.client.get(reverse('payments:mpesa-push'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('users:customer_send_otp')))

    def test_payment_push_redirects_to_cart_when_session_empty(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('payments:mpesa-push'))
        self.assertRedirects(response, reverse('orders:cart_detail'))

    @patch('payments.views.MpesaClient')
    def test_payment_push_success_renders_pending_template(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.stk_push.return_value = {
            'ResponseCode': '0',
            'CheckoutRequestID': 'ws_CO_123456789',
            'CustomerMessage': 'Success. Request accepted for processing'
        }

        self.client.force_login(self.customer)
        session = self.client.session
        session['pending_order_id'] = self.order.id
        session['order_total'] = str(self.order.total_price)
        session['order_phone'] = self.customer.phone_no
        session.save()

        response = self.client.get(reverse('payments:mpesa-push'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/payment_pending.html')
        self.assertContains(response, 'ws_CO_123456789')
        self.assertContains(response, '254712345678')

        # Check transaction created
        tx = MpesaTransaction.objects.get(checkout_request_id='ws_CO_123456789')
        self.assertEqual(tx.order, self.order)
        self.assertEqual(tx.status, 'PENDING')

    def test_check_payment_status_endpoint(self):
        tx = MpesaTransaction.objects.create(
            order=self.order,
            checkout_request_id='ws_CO_999',
            amount=Decimal('1050.00'),
            phone_number='254712345678',
            status='PENDING'
        )
        response = self.client.get(reverse('payments:check-payment-status'), {'checkout_request_id': 'ws_CO_999'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data.get('transaction_status'), 'PENDING')
