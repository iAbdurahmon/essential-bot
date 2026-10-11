from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode
from aiogram import F

from lg_messages.func import lg_check
from keyboards.reply import func_kb
from data_small import *
from utils.states import Poll_state
from dialogs.poll import Poll_manager

router = Router()


async def book(message: Message, state: FSMContext):
    await message.answer(lg_check("Choose a book:", "Выберите книгу:", "Kitobni tanlang:", message),
                         reply_markup=func_kb(lg_check(book_names_en,
                                                       book_names_ru,
                                                       book_names_uz,
                                                       message), message))
    await state.set_state(Poll_state.dialog_start)


@router.message(Poll_state.dialog_start, F.text.in_(book_names_all))
async def dialog_start_for_poll(message: Message, state: FSMContext, dialog_manager: DialogManager):
    text = message.text[-1]
    text_list = [lg_check("🔙 Back", "🔙 Назад", "🔙 Orqaga", message),
                 lg_check("🏠 Main Menu", "🏠 Главное Меню", "🏠 Asosiy Menyu", message)]

    message_text = await message.answer(lg_check("Choose the Units", "Выберите Unit", "Unitlarni tanlang", message),
                                        reply_markup=func_kb(text_list, message))

    message_id = message_text.message_id
    text_for_edit['editer'] = message_id
    await state.set_state(Poll_state.dialog_started)
    data = [text]
    await dialog_manager.start(Poll_manager.unit_select, mode=StartMode.RESET_STACK, data=data)
