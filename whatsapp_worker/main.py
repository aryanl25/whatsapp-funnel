import logging
from typing import Mapping, Tuple
from whatsapp_worker.config import config
from whatsapp_worker.send import send_whatsapp_text
from server.database import SessionLocal
from server.services.whatsapp import handle_incoming_message
import boto3
import json
import time

logger = logging.getLogger(__name__)

# --- SQS Client Initialization ---
sqs = boto3.client(
    'sqs',
    region_name=config.AWS_REGION,
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
)


def start_worker():
    """
    Infinite loop to pull messages from SQS and pass them to handle_webhook.
    """
    logger.info(f"Worker started. Listening on: {config.QUEUE_URL}")

    while True:
        try:
            # Long Polling: Wait up to 20 seconds for a message
            response = sqs.receive_message(
                QueueUrl=config.QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20,
                VisibilityTimeout=30  # Message is hidden for 30s while we process
            )

            messages = response.get('Messages', [])
            if not messages:
                continue

            for message in messages:
                receipt_handle = message['ReceiptHandle']
                
                body = json.loads(message['Body'])
                
                result_body, status_code = handle_webhook(body)

                if status_code == 200:
                    sqs.delete_message(
                        QueueUrl=config.QUEUE_URL,
                        ReceiptHandle=receipt_handle
                    )
                else:
                    logger.warning(f"Processing failed with {status_code}. Message will be retried by SQS.")

        except Exception as e:
            logger.error(f"Worker Loop Error: {e}")
            time.sleep(5) # Cooldown before retrying loop

def handle_webhook(body: Mapping) -> Tuple[Mapping, int]:
    try:
        value = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
        
        if value.get("statuses"):
            return {"status": "ok"}, 200

        messages = value.get("messages")
        if not messages:
            return {"status": "ok"}, 200

        msg = messages[0]
        whatsapp_id = msg.get("id")
        
        contacts = value.get("contacts", [])
        sender_waid = contacts[0].get("wa_id") if contacts and len(contacts) > 0 else msg.get("from")
        
        text_body = None
        
        if msg.get("type") == "text":
            text_body = msg["text"]["body"]

        if text_body:
            logger.info(f"Received from {sender_waid}: {text_body}")
            
            # Process message using service
            db = SessionLocal()
            try:
                ai_response = handle_incoming_message(db, sender_waid, text_body, contacts)
                if ai_response:
                    send_whatsapp_text(sender_waid, ai_response)
            finally:
                db.close()
                
        return {"status": "ok"}, 200
        
    except Exception as e:
        logger.error(f"Webhook handling error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    start_worker()