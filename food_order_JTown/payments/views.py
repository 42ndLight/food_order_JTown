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

# Initialize Daraja client
class MpesaPaymentView(View):
    def get(self, request, *args, **kwargs):
        """Initiate M-Pesa STK push payment"""
        try:
            # Get order details from session
            order_id = request.session.get('pending_order_id')
            order_total = request.session.get('order_total')
            order_phone = request.session.get('order_phone')
            
            if not all([order_id, order_total, order_phone]):
                messages.error(request, "Order information not found. Please try again.")
                return redirect('orders:cart_detail')
            
            cl = MpesaClient()
            # Get the order object
            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                messages.error(request, "Order not found.")
                return redirect('orders:cart_detail')
            
            # Prepare phone number (ensure it's in correct format)
            phone_number = str(order_phone).strip()
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]  # Convert 07XX to 2547XX
            elif phone_number.startswith('+254'):
                phone_number = phone_number[1:]  # Remove + sign
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            # Convert amount to integer (M-Pesa requires integer)
            amount = int(float(order_total))
            
            # M-Pesa STK Push parameters
            cl = MpesaClient()
            account_reference = f"Order-{order.id}"
            transaction_desc = f"Payment for Order {order.id}"
            callback_url = f"{settings.MPESA_CALLBACK_URL}/pay"
            logger.info(f"Initiating M-Pesa payment: Order={order.id}, Amount={amount}, Phone={phone_number}")
            
            
            try:
                response = cl.stk_push(
                    phone_number=phone_number,
                    amount=amount,
                    account_reference=account_reference,
                    transaction_desc=transaction_desc,
                    callback_url=callback_url
                )
                
                logger.debug(f"Response type: {type(response)}")
                logger.debug(f"Response object: {response}")
                
                # Handle different response types
                if hasattr(response, 'response_data'):
                    response_data = response.response_data
                elif hasattr(response, '__dict__'):
                    response_data = response.__dict__
                elif isinstance(response, dict):
                    response_data = response
                else:
                    # Try to convert to dict
                    try:
                        response_data = vars(response)
                    except:
                        response_data = {}
                
                logger.debug(f"M-Pesa Response Data: {response_data}")
                
                # Check response code
                response_code = str(response_data.get('ResponseCode', ''))
                
                if response_code == '0':
                    checkout_request_id = response_data.get('CheckoutRequestID')
                    
                    if not checkout_request_id:
                        logger.error("No CheckoutRequestID in successful response")
                        messages.error(request, "Payment initiation failed. Please try again.")
                        return redirect('orders:checkout')
                    
                    # Create MpesaTransaction record
                    mpesa_transaction = MpesaTransaction.objects.create(
                        order=order,
                        checkout_request_id=checkout_request_id,
                        amount=Decimal(str(amount)),
                        phone_number=phone_number,
                        status='PENDING'
                    )
                    
                    logger.info(f"M-Pesa transaction created: ID={mpesa_transaction.id}, CheckoutRequestID={checkout_request_id}")
                    
                    # Store checkout request ID in session
                    request.session['checkout_request_id'] = checkout_request_id
                    
                    messages.success(request, "Payment request sent! Please check your phone and enter your M-Pesa PIN.")
                    
                    context = {
                        'order': order,
                        'amount': amount,
                        'phone_number': phone_number,
                        'checkout_request_id': checkout_request_id,
                    }
                    return render(request, 'payments/payment_pending.html', context)
                    
                else:
                    # Handle API error
                    error_message = (
                        response_data.get('errorMessage') or 
                        response_data.get('CustomerMessage') or 
                        response_data.get('ResponseDescription') or
                        'Payment initiation failed'
                    )
                    error_code = response_data.get('errorCode') or response_data.get('ResponseCode', 'Unknown')
                    
                    logger.error(f"M-Pesa API Error: Code={error_code}, Message={error_message}")
                    logger.error(f"Full response: {response_data}")
                    
                    messages.error(request, f"Payment failed: {error_message}")
                    return redirect('orders:order_create')
                    
            except Exception as api_error:
                logger.error(f"M-Pesa API call failed: {str(api_error)}", exc_info=True)
                messages.error(request, "Could not connect to M-Pesa. Please try again later.")
                return redirect('orders:order_create')
                
        except Exception as e:
            logger.error(f"Payment initiation error: {str(e)}", exc_info=True)
            messages.error(request, "Payment initiation failed. Please try again.")
            return redirect('orders:order_create')


def check_payment_status(request):
    """AJAX endpoint to check payment status"""
    if request.method == 'GET':
        checkout_request_id = request.GET.get('checkout_request_id')
        
        if not checkout_request_id:
            return JsonResponse({'status': 'error', 'message': 'Missing checkout request ID'})
        
        try:
            mpesa_transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
            order = mpesa_transaction.order
            
            return JsonResponse({
                'status': 'success',
                'transaction_status': mpesa_transaction.status,
                'order_status': order.status,
                'order_id': order.id
            })
        except MpesaTransaction.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Transaction not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})


@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa webhook callback to update order status."""
    logger.info("Received M-Pesa callback")
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body)
            result_code = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
            checkout_request_id = callback_data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
            
            # Extract M-Pesa receipt number if payment was successful
            mpesa_receipt_number = None
            if result_code == 0:
                callback_metadata = callback_data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {})
                items = callback_metadata.get('Item', [])
                for item in items:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        mpesa_receipt_number = item.get('Value')
                        break
            
            logger.debug(f"Callback data: ResultCode={result_code}, CheckoutRequestID={checkout_request_id}")

            if not checkout_request_id:
                logger.error("Invalid callback data: No CheckoutRequestID")
                return HttpResponse("Invalid callback data", status=400)

            with transaction.atomic():
                mpesa_transaction = MpesaTransaction.objects.select_for_update().get(checkout_request_id=checkout_request_id)
                order = mpesa_transaction.order
                mpesa_transaction.callback_data = callback_data

                if result_code == 0:
                    mpesa_transaction.status = 'SUCCESS'
                    mpesa_transaction.mpesa_receipt_number = mpesa_receipt_number or ''
                    order.status = 'paid'
                    # Optional: Update loyalty points
                    if order.user:
                        order.user.loyalty_points += int(float(order.total_price)) // 10  # 1 point per KSh 10
                        order.user.save()
                else:
                    mpesa_transaction.status = 'FAILED'
                    order.status = 'failed'

                mpesa_transaction.save()
                order.save()
                logger.info(f"Updated transaction: ID={mpesa_transaction.id}, Status={mpesa_transaction.status}, Order Status={order.status}")
                
        except MpesaTransaction.DoesNotExist:
            logger.error(f"Transaction not found for CheckoutRequestID={checkout_request_id}")
            return HttpResponse("Transaction not found", status=404)
        except Exception as e:
            logger.error(f"Callback processing failed: {str(e)}", exc_info=True)
            return HttpResponse(f"Error: {str(e)}", status=500)

        return HttpResponse("Callback received", status=200)
    return HttpResponse("Method not allowed", status=405)