"""
Webhook server for Pushin Pay payment notifications
Handles incoming webhook requests from Pushin Pay API
"""

import logging
import json
import sqlite3
from aiohttp import web
from aiohttp.web import Request, Response
from app.pushinpay_integration import pushinpay_client
from app.users_db import user_db

logger = logging.getLogger(__name__)


async def pushinpay_webhook_handler(request: Request) -> Response:
    """
    Handle incoming webhook from Pushin Pay
    
    Expected payload structure:
    {
        "event": "charge.paid",
        "data": {
            "id": "charge_id",
            "status": "paid",
            "reference_id": "user_123_plan_lifetime_1234567890",
            "amount": 5990,
            "currency": "BRL"
        }
    }
    """
    try:
        # Get signature from headers
        signature = request.headers.get('X-PushinPay-Signature', '')
        if not signature:
            logger.warning("Webhook request missing signature")
            return web.Response(status=401, text="Missing signature")
        
        # Read raw body for signature verification
        body = await request.read()
        
        # Verify webhook signature
        if not pushinpay_client.verify_webhook_signature(signature, body):
            logger.warning("Invalid webhook signature")
            return web.Response(status=401, text="Invalid signature")
        
        # Parse JSON payload
        try:
            payload = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook: {e}")
            return web.Response(status=400, text="Invalid JSON")
        
        event_type = payload.get('event')
        data = payload.get('data', {})
        
        logger.info(f"Received webhook event: {event_type} for charge {data.get('id')}")
        
        # Handle different event types
        if event_type == 'charge.paid':
            charge_id = data.get('id')
            reference_id = data.get('reference_id', '')
            status = data.get('status')
            
            if not charge_id:
                logger.error("Webhook missing charge ID")
                return web.Response(status=400, text="Missing charge ID")
            
            # Extract user_id and plan_type from reference_id
            # Format: user_{user_id}_plan_{plan_type}_{timestamp}
            try:
                ref_parts = reference_id.split('_')
                if len(ref_parts) >= 4 and ref_parts[0] == 'user':
                    user_id = int(ref_parts[1])
                    plan_type = ref_parts[3]
                    
                    # Check if transaction exists (idempotency check) using async helpers
                    existing_trans = await user_db.async_get_transaction(charge_id)
                    if not existing_trans and reference_id:
                        # Try lookup by reference_id
                        existing_trans = await user_db.async_get_transaction(reference_id)
                        if existing_trans:
                            # Try to update to provider id for future idempotency
                            try:
                                await user_db.async_update_transaction_id(reference_id, charge_id)
                                logger.info(f"Updated transaction id from reference {reference_id} to provider id {charge_id}")
                            except Exception as e:
                                logger.warning(f"Could not update transaction id from {reference_id} to {charge_id}: {e}")

                    if existing_trans:
                        existing_status = existing_trans.get('status')
                        if existing_status == 'PAID':
                            logger.info(f"Transaction {charge_id} already processed, skipping duplicate webhook")
                            return web.Response(status=200, text="Already processed")
                    
                    # Update transaction status (idempotent)
                    await user_db.async_update_transaction_status(
                        transaction_id=charge_id,
                        status='PAID',
                        status_detail='Payment confirmed via webhook'
                    )
                    
                    # Activate license (idempotent - safe to call multiple times)
                    await user_db.async_activate_license(user_id, plan_type)
                    
                    logger.info(f"License {plan_type} activated for user {user_id} via Pushin Pay webhook")
                    
                    # Note: User notification is handled by the manual check button
                    # Users can click "Já Paguei" button to verify payment status
                    # Webhook automatically activates the license in the background
                    
                    return web.Response(status=200, text="OK")
                else:
                    logger.error(f"Invalid reference_id format: {reference_id}")
                    return web.Response(status=400, text="Invalid reference_id format")
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing reference_id {reference_id}: {e}")
                return web.Response(status=400, text="Error parsing reference_id")
        
        elif event_type == 'charge.failed':
            charge_id = data.get('id')
            if charge_id:
                await user_db.async_update_transaction_status(
                    transaction_id=charge_id,
                    status='FAILED',
                    status_detail='Payment failed'
                )
                logger.info(f"Charge {charge_id} marked as failed")
            return web.Response(status=200, text="OK")
        
        elif event_type == 'charge.expired':
            charge_id = data.get('id')
            if charge_id:
                await user_db.async_update_transaction_status(
                    transaction_id=charge_id,
                    status='EXPIRED',
                    status_detail='Payment expired'
                )
                logger.info(f"Charge {charge_id} marked as expired")
            return web.Response(status=200, text="OK")
        
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
            return web.Response(status=200, text="Event type not handled")
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return web.Response(status=500, text="Internal server error")


def create_webhook_app() -> web.Application:
    """Create aiohttp web application for webhooks"""
    app = web.Application()
    app.router.add_post('/pushinpay_webhook', pushinpay_webhook_handler)
    return app


async def start_webhook_server(port: int = 8080):
    """Start the webhook server"""
    app = create_webhook_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Webhook server started on port {port}")
    return runner
