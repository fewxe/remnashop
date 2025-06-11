from datetime import datetime
from decimal import Decimal

from aiogram import html
from aiogram.utils.link import create_tg_link

from app.core.enums import UserRole

from .base import TrackableModel


class UserDto(TrackableModel):
    id: int
    telegram_id: int
    name: str
    role: UserRole
    language: str
    balance: Decimal
    personal_discount: float
    purchase_discount: float
    is_blocked: bool
    is_bot_blocked: bool
    is_trial_used: bool
    created_at: datetime
    updated_at: datetime

    @property
    def url(self) -> str:
        return create_tg_link("user", id=self.id)

    @property
    def mention(self) -> str:
        return html.link(value=self.name, link=self.url)
