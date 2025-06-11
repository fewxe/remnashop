from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row, Select, Start, SwitchTo
from aiogram_dialog.widgets.text import Format

from app.bot.states import DashboardState, RemnashopState
from app.bot.widgets import Banner, I18nFormat, IgnoreInput
from app.core.enums import BannerName

from .getters import admins_getter

remnashop = Window(
    Banner(BannerName.DASHBOARD),
    I18nFormat("msg-remnashop"),
    Row(
        SwitchTo(
            I18nFormat("btn-remnashop-admins"),
            id="remnashop.admins",
            state=RemnashopState.admins,
        )
    ),
    Row(
        SwitchTo(
            I18nFormat("btn-remnashop-referral"),
            id="remnashop.referral",
            state=RemnashopState.referral,
        ),
        SwitchTo(
            I18nFormat("btn-remnashop-ads"),
            id="remnashop.ads",
            state=RemnashopState.ads,
        ),
    ),
    Row(
        SwitchTo(
            I18nFormat("btn-remnashop-plans"),
            id="remnashop.plans",
            state=RemnashopState.plans,
        ),
        SwitchTo(
            I18nFormat("btn-remnashop-notifications"),
            id="remnashop.notifications",
            state=RemnashopState.notifications,
        ),
    ),
    Row(
        Button(
            I18nFormat("btn-remnashop-logs"),
            id="remnashop.logs",
        ),
        Button(
            I18nFormat("btn-remnashop-audit"),
            id="remnashop.audit",
        ),
    ),
    Row(
        Start(
            I18nFormat("btn-back"),
            id="back.dashboard",
            state=DashboardState.main,
        )
    ),
    IgnoreInput(),
    state=RemnashopState.main,
)


async def on_admin_selected(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    selected_item: str,
):
    await callback.answer(f"Выбран админ: {selected_item}")


async def on_admin_removed(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    selected_item: str,
):
    await callback.answer(f"Удалить админа: {selected_item}")


admins = Window(
    Banner(BannerName.DASHBOARD),
    I18nFormat("msg-remnashop-admins"),
    Group(
        Select(
            text=I18nFormat(
                "btn-remnashop-admin",
                role=Format("{item.role}"),
                id=Format("{item.telegram_id}"),
            ),
            id="select_admin",
            item_id_getter=lambda item: item.telegram_id,
            items="admins",
            on_click=on_admin_selected,
        ),
        Select(
            text=Format("❌"),
            id="remove_admin",
            item_id_getter=lambda item: item.telegram_id,
            items="admins",
            on_click=on_admin_removed,
        ),
        width=2,
    ),
    # Select(
    #     text=I18nFormat(
    #         "btn-remnashop-admin",
    #         role=Format("{item.role}"),
    #         id=Format("{item.telegram_id}"),
    #         name=Format("{item.name}"),
    #     ),
    #     id="remnashop.admin",
    #     items="admins",
    #     item_id_getter=lambda item: item.telegram_id,
    #     on_click=on_admin_selected,
    # ),
    Row(
        Start(
            I18nFormat("btn-back"),
            id="back.remnashop",
            state=RemnashopState.main,
        )
    ),
    IgnoreInput(),
    state=RemnashopState.admins,
    getter=admins_getter,
)


router = Dialog(
    remnashop,
    admins,
)
