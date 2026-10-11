from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from data_small import book_names_all, text_for_edit
from utils.states import Func1, Books
from dialogs.dialog import Unit
from lg_messages.func import lg_check
from keyboards.reply import func_kb

router = Router()


@router.message(Func1.choose_book, F.text.in_(book_names_all))
async def book_filter(message: Message, state: FSMContext, dialog_manager: DialogManager):
    text = message.text[-1]

    text_list = [lg_check("🔙 Back", "🔙 Назад", "🔙 Orqaga", message),
                 lg_check("🏠 Main Menu", "🏠 Главное Меню", "🏠 Asosiy Menyu", message)]

    message_text = await message.answer(lg_check("Choose the Units", "Выберите Unit", "Unitlarni tanlang", message),
                         reply_markup=func_kb(text_list, message))
    message_id = message_text.message_id
    text_for_edit['editer'] = message_id
    await state.set_state(Books.books)
    data = [text]
    await dialog_manager.start(Unit.unit_state, mode=StartMode.RESET_STACK, data=data)






