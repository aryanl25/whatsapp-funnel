import json
import logging
from typing import Mapping, Tuple
import requests
from whatsapp_worker.config import config

logger = logging.getLogger(__name__)

def _api_url() -> str:
    return f"https://graph.facebook.com/{config.VERSION}/{config.PHONE_NUMBER_ID}/messages"

def _get_text_payload(recipient: str, text: str) -> str:
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

def send_whatsapp_text(
    to: str, 
    text: str
) -> Tuple[Mapping, int]:
    """
    Sends a WhatsApp message.
    
    Arguments:
        to (str): The recipient's phone number.
        text (str): The message body.
        config (WhatsAppSendConfig, optional): Dependency injection for config.
    """
    recipient = to
    
    # Validation
    if not (config.ACCESS_TOKEN and config.VERSION and config.PHONE_NUMBER_ID and recipient):
        logger.error("Missing WhatsApp configuration or recipient")
        return {"status": "error", "message": "Missing configuration"}, 500

    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {config.ACCESS_TOKEN}",
    }

    try:
        # Timeout increased to 15s
        resp = requests.post(
            _api_url(), 
            data=_get_text_payload(recipient, text), 
            headers=headers, 
            timeout=15
        )
        resp.raise_for_status()
        return resp.json(), resp.status_code

    except requests.Timeout:
        logger.error("WhatsApp request timed out")
        return {"status": "error", "message": "Request timed out"}, 408

    except requests.RequestException as e:
        logger.error(f"WhatsApp send error: {e}")
        
        if 'resp' in locals():
             try:
                 return resp.json(), resp.status_code
             except Exception:
                 pass # Fall through to generic error
        return {"status": "error", "message": "Failed to send message"}, 500
