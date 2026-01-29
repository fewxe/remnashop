import uuid
from decimal import Decimal
from typing import Any, Final
from uuid import UUID

import orjson
from aiogram import Bot
from fastapi import Request
from httpx import AsyncClient, HTTPStatusError
from loguru import logger

from src.core.config import AppConfig
from src.core.enums import Currency, TransactionStatus
from src.infrastructure.database.models.dto import (
    PaymentGatewayDto,
    PaymentResult,
    PlategaGatewaySettingsDto,
)

from .base import BasePaymentGateway


class PlategaGateway(BasePaymentGateway):
    _client: AsyncClient

    API_BASE: Final[str] = "https://app.platega.io"
    CURRENCY = Currency.RUB
    PAYMENT_METHOD: Final[int] = 2

    def __init__(self, gateway: PaymentGatewayDto, bot: Bot, config: AppConfig) -> None:
        super().__init__(gateway, bot, config)

        if not isinstance(self.data.settings, PlategaGatewaySettingsDto):
            raise TypeError(
                f"Invalid settings type: expected {PlategaGatewaySettingsDto.__name__}, "
                f"got {type(self.data.settings).__name__}"
            )

        self._client = self._make_client(
            base_url=self.API_BASE,
            headers={
                "X-MerchantId": self.data.settings.merchant_id,
                "X-Secret": self.data.settings.api_key.get_secret_value(),  # type: ignore[union-attr]
            },
        )

    async def handle_create_payment(self, amount: Decimal, details: str) -> PaymentResult:
        payload = await self._create_payment_payload(str(amount), details)

        try:
            response = await self._client.post("/transaction/process", json=payload)
            response.raise_for_status()
            data = orjson.loads(response.content)
            return self._get_payment_data(data)

        except HTTPStatusError as exception:
            logger.error(
                f"HTTP error creating payment. "
                f"Status: '{exception.response.status_code}', Body: {exception.response.text}"
            )
            raise
        except (KeyError, orjson.JSONDecodeError) as exception:
            logger.error(f"Failed to parse response. Error: {exception}")
            raise
        except Exception as exception:
            logger.exception(f"An unexpected error occurred while creating payment: {exception}")
            raise

    async def handle_webhook(self, request: Request) -> tuple[UUID, TransactionStatus]:
        logger.debug(f"Received {self.__class__.__name__} webhook request")

        if not self._verify_webhook(request):
            raise PermissionError("Webhook verification failed")

        webhook_data = await self._get_webhook_data(request)

        transaction_id_str = webhook_data.get("id")
        status = webhook_data.get("status")

        if not transaction_id_str:
            raise ValueError("Required field 'id' is missing")

        if not status:
            raise ValueError("Required field 'status' is missing")

        transaction_id = UUID(transaction_id_str)
        transaction_status = self._map_status(status)

        logger.info(
            f"Platega webhook processed: "
            f"transaction_id={transaction_id}, "
            f"status={transaction_status}"
        )
        return transaction_id, transaction_status

    async def _create_payment_payload(
        self, amount: str, details: str
    ) -> dict[str, Any]:
        return {
            "paymentMethod": self.PAYMENT_METHOD,
            "paymentDetails": {
                "amount": amount,
                "currency": self.CURRENCY.value,
            },
            "description": details,
            "return": await self._get_bot_redirect_url(),
            "failedUrl": await self._get_bot_redirect_url(),
        }
    
    def _get_payment_data(self, data: dict[str, Any]) -> PaymentResult:
        transaction_id = data.get("transactionId")

        if not transaction_id:
            raise KeyError("Invalid response from Platega API: missing 'transactionId'")

        redirect_url = data.get("redirect")

        if not redirect_url:
            raise KeyError("Invalid response from Platega API: missing 'redirect'")

        return PaymentResult(id=UUID(transaction_id), url=str(redirect_url))

    def _verify_webhook(self, request: Request) -> bool:
        merchant_id = request.headers.get("X-MerchantId")
        secret = request.headers.get("X-Secret")

        if not merchant_id:
            logger.warning("Missing X-MerchantId header")
            return False

        if not secret:
            logger.warning("Missing X-Secret header")
            return False

        if merchant_id != self.data.settings.merchant_id:  # type: ignore[union-attr]
            logger.warning(
                f"Invalid X-MerchantId: "
                f"expected {self.data.settings.merchant_id}, got {merchant_id}"  # type: ignore[union-attr]
            )
            return False

        if secret != self.data.settings.api_key.get_secret_value():  # type: ignore[union-attr]
            logger.warning("Invalid X-Secret")
            return False

        return True

    def _map_status(self, status: str) -> TransactionStatus:
        status_mapping = {
            "CONFIRMED": TransactionStatus.COMPLETED,
            "CANCELED": TransactionStatus.CANCELED
        }

        if status not in status_mapping:
            raise ValueError(f"Unsupported status: {status}")

        return status_mapping[status]
