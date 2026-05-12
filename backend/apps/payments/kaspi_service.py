import requests
import uuid
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class KaspiPayService:
    BASE_URL_TEST = "https://mtokentest.kaspi.kz:8543/r1/v01"
    BASE_URL_PROD = "https://mtoken.kaspi.kz:8543/r1/v01"

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = self.BASE_URL_PROD if api_key.startswith("prod_") else self.BASE_URL_TEST

    def _get_headers(self):
        return {
            "Api-Key": self.api_key,
            "X-Request-ID": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }

    def get_trade_points(self):
        """
        Get list of trade points to select one for device registration.
        """
        url = f"{self.base_url}/partner/tradepoints"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("StatusCode") == 0:
                return data.get("Data", [])
            else:
                logger.error(f"Kaspi API Error (get_trade_points): {data}")
                return None
        except Exception as e:
            logger.exception(f"Kaspi request failed (get_trade_points): {e}")
            return None

    def register_device(self, device_id, trade_point_id):
        """
        Register a virtual device to get a DeviceToken.
        """
        url = f"{self.base_url}/device/register"
        payload = {
            "DeviceId": device_id,
            "TradePointId": trade_point_id
        }
        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("StatusCode") == 0:
                return data.get("Data", {}).get("DeviceToken")
            else:
                logger.error(f"Kaspi API Error (register_device): {data}")
                return None
        except Exception as e:
            logger.exception(f"Kaspi request failed (register_device): {e}")
            return None

    def create_payment_link(self, device_token, amount, external_id=None):
        """
        Create a payment link for QR payment.
        """
        url = f"{self.base_url}/qr/create-link"
        payload = {
            "DeviceToken": device_token,
            "Amount": float(amount),
        }
        if external_id:
            payload["ExternalId"] = str(external_id)

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("StatusCode") == 0:
                return data.get("Data")
            else:
                logger.error(f"Kaspi API Error (create_payment_link): {data}")
                return None
        except Exception as e:
            logger.exception(f"Kaspi request failed (create_payment_link): {e}")
            return None

    def get_payment_status(self, qr_payment_id):
        """
        Check status of a payment.
        """
        url = f"{self.base_url}/payment/status/{qr_payment_id}"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("StatusCode") == 0:
                return data.get("Data", {}).get("Status")
            else:
                logger.error(f"Kaspi API Error (get_payment_status): {data}")
                return None
        except Exception as e:
            logger.exception(f"Kaspi request failed (get_payment_status): {e}")
            return None
