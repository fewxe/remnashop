from aiogram.types import Message
from aiogram_dialog import DialogManager, DialogProtocol, ShowMode
from aiogram_dialog.widgets.input import BaseInput


class IgnoreInput(BaseInput):
    async def process_message(
        self,
        message: Message,
        dialog: DialogProtocol,
        dialog_manager: DialogManager,
    ) -> bool:
        dialog_manager.show_mode = ShowMode.NO_UPDATE
        return True
