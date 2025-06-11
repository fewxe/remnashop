from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row, Start

from app.bot.conditions import is_admin
from app.bot.states import DashboardState, MenuState
from app.bot.widgets import Banner, I18nFormat, IgnoreInput
from app.core.enums import BannerName
from app.db.models import UserDto


async def getter(dialog_manager: DialogManager, user: UserDto, **kwargs):
    return {
        "id": str(user.telegram_id),
        "name": user.name,
        "balance": user.balance,
        "status": "none",
    }


router = Dialog(
    Window(
        Banner(BannerName.MENU),
        I18nFormat("msg-menu-profile"),
        I18nFormat("space"),
        I18nFormat("msg-menu-subscription"),
        Row(Button(I18nFormat("btn-menu-connect"), id="menu.connect")),
        # Row(Button(I18nFormat("btn-menu-trial"), id="menu.trial")),
        Row(
            Button(I18nFormat("btn-menu-balance"), id="menu.balance"),
            Button(I18nFormat("btn-menu-subscription"), id="menu.subscription"),
        ),
        Row(
            Button(I18nFormat("btn-menu-invite"), id="menu.invite"),
            Button(I18nFormat("btn-menu-support"), id="menu.support"),
        ),
        # Row(Button(I18nFormat("btn-menu-promocode"), id="menu.promocode")),
        Row(
            Start(
                I18nFormat("btn-menu-dashboard"),
                id="menu.dashboard",
                state=DashboardState.main,
                when=is_admin,
            )
        ),
        IgnoreInput(),
        state=MenuState.main,
        getter=getter,
    )
)
