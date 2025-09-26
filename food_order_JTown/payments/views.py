from django_daraja.mpesa.core import MpesaClient
import json
from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.conf import settings
from orders.models import Order
from .models import MpesaTransaction
import logging
from orders.views import get_cart

logger = logging.getLogger(__name__)

# Initialize Daraja


@login_required
class MpesaPaymentView(View):
	pass
    

@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa webhook callback to update order status."""
    logger.info("Received M-Pesa callback")
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body)
            result_code = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
            checkout_request_id = callback_data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
            logger.debug(f"Callback data: ResultCode={result_code}, CheckoutRequestID={checkout_request_id}")

            if not checkout_request_id:
                logger.error("Invalid callback data: No CheckoutRequestID")
                return HttpResponse("Invalid callback data", status=400)

            with transaction.atomic():
                transaction = MpesaTransaction.objects.select_for_update().get(checkout_request_id=checkout_request_id)
                order = transaction.order
                transaction.callback_data = callback_data

                if result_code == 0:
                    transaction.status = 'SUCCESS'
                    order.status = 'paid'
                    # Optional: Update loyalty points
                    order.user.loyalty_points += int(float(order.total_price)) // 10  # 1 point per KSh 10
                    order.user.save()
                else:
                    transaction.status = 'FAILED'
                    order.status = 'failed'

                transaction.save()
                order.save()
                logger.info(f"Updated transaction: ID={transaction.id}, Status={transaction.status}, Order Status={order.status}")
        except MpesaTransaction.DoesNotExist:
            logger.error(f"Transaction not found for CheckoutRequestID={checkout_request_id}")
            return HttpResponse("Transaction not found", status=404)
        except Exception as e:
            logger.error(f"Callback processing failed: {str(e)}", exc_info=True)
            return HttpResponse(f"Error: {str(e)}", status=500)

        return HttpResponse("Callback received", status=200)
    return HttpResponse("Method not allowed", status=405)