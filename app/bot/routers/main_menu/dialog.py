from aiogram_dialog import Dialog, Window

from app.bot.states import MainMenuState, ProfileState
from app.bot.widgets import I18NFormat, IgnoreInput

dialog = Dialog(
    Window(
        I18NFormat("main_menu"),
        # Row(
        #     Start(
        #         text=Const("Profile"),
        #         id="profile",
        #         state=ProfileState.profile,
        #     ),
        # ),
        IgnoreInput(),
        state=MainMenuState.main_menu,
    ),
)
