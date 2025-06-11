from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo

from app.bot.models.containers import AppContainer
from app.bot.states import DashboardState, RemnawaveState
from app.bot.widgets import Banner, I18nFormat, IgnoreInput
from app.core.constants import APP_CONTAINER_KEY
from app.core.enums import BannerName

users = Window(
    Banner(BannerName.DASHBOARD),
    I18nFormat("msg-dashboard-users"),
    Row(
        Button(
            I18nFormat("btn-users-search"),
            id="users.search",
        )
    ),
    Row(
        Button(
            I18nFormat("btn-users-recent-registered"),
            id="users.recent_registered",
        )
    ),
    Row(
        Button(
            I18nFormat("btn-users-recent-activity"),
            id="users.recent_activity",
        )
    ),
    Row(
        SwitchTo(
            I18nFormat("btn-users-banlist"),
            id="users.banlist",
            state=DashboardState.banlist,
        )
    ),
    Row(
        SwitchTo(
            I18nFormat("btn-back"),
            id="back.dashboard",
            state=DashboardState.main,
        )
    ),
    IgnoreInput(),
    state=DashboardState.users,
)

banlist = Window(
    Banner(BannerName.DASHBOARD),
    I18nFormat("msg-users-banlist"),
    Row(
        Button(
            I18nFormat("btn-banlist-unblock-all"),
            id="banlist.unblock_all",
        )
    ),
    Row(
        SwitchTo(
            I18nFormat("btn-back"),
            id="back.dashboard",
            state=DashboardState.users,
        )
    ),
    IgnoreInput(),
    state=DashboardState.banlist,
)

router = Dialog(
    users,
)
