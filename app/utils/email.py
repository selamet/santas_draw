import logging
import requests
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


def _get_access_token() -> Optional[str]:
    """
    Get access token from SendPulse OAuth endpoint

    Returns:
        Access token string or None if failed
    """
    # TODO: Cache the access token until it expires to avoid frequent requests


def send_draw_result_email(
        participant_name: str,
        participant_email: str,
        receiver_name: str,
        receiver_address: Optional[str] = None,
        receiver_phone: Optional[str] = None
) -> bool:
    """
    Send draw result email to participant using SendPulse REST API with template

    Args:
        participant_name: Name of the participant (giver)
        participant_email: Email of the participant
        receiver_name: Name of the receiver
        receiver_address: Address of the receiver (optional)
        receiver_phone: Phone of the receiver (optional)

    Returns:
        True if email sent successfully, False otherwise
    """
    if not settings.sendpulse_template_id:
        logger.error("SendPulse template ID not configured")
        return False

    if not settings.sendpulse_from_email:
        logger.error("SendPulse from_email not configured")
        return False

    access_token = _get_access_token()

    if not access_token:
        return False

    template_variables: Dict[str, Any] = {
        "participant_name": participant_name,
        "receiver_name": receiver_name,
    }

    if receiver_address:
        template_variables["receiver_address"] = receiver_address

    if receiver_phone:
        template_variables["receiver_phone"] = receiver_phone

    try:
        email_payload = {
            "email": {
                "from": {
                    "name": settings.sendpulse_from_name,
                    "email": settings.sendpulse_from_email
                },
                "to": [
                    {
                        "email": participant_email,
                        "name": participant_name
                    }
                ],
                "template": {
                    "id": settings.sendpulse_template_id,
                    "variables": template_variables
                }
            }
        }

        response = requests.post(
            settings.sendpulse_email_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=email_payload,
            timeout=30
        )
        response.raise_for_status()

        logger.info(
            f"Email sent successfully to {participant_email} "
            f"using template {settings.sendpulse_template_id}"
        )
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send email to {participant_email}: {e}")

        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                logger.error(f"SendPulse API error: {error_detail}")
            except:
                logger.error(f"SendPulse API error response: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email to {participant_email}: {e}")
        return False
