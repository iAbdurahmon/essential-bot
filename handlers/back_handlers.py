from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram_dialog import DialogManager

from data_small import *
from utils.states import *
from handlers.start import start
from funcs import list_book, book, profile_start
from Poll import polling

router = Router()


@router.message(F.text.in_(main_menu))
async def main_menu(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.reset_stack()
    await state.set_state(Status.on)
    await start(message, state)


@router.message(Func1.choose_book, F.text.in_(backs))
async def choose_book_or_list_backs(message: Message, state: FSMContext):
    await list_book(message, state)


@router.message(Books.books, F.text.in_(backs))
async def unit_backs(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.done()
    await book(message, state)


@router.message(Func1.choose_book_or_list, F.text.in_(backs))
@router.message(Poll_state.dialog_start, F.text.in_(backs))
@router.message(Translate.from_lg, F.text.in_(backs))
@router.message(Translate.to_lg, F.text.in_(backs))
@router.message(Profile.profile_start, F.text.in_(backs))
async def mix_start_back(message: Message, state: FSMContext):
    await start(message, state)


@router.message(Poll_state.dialog_started, F.text.in_(backs))
async def quiz_back(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.reset_stack()
    await state.clear()
    await polling.book(message, state)


@router.message(Profile.rating, F.text.in_(backs))
async def to_profile(message: Message, state: FSMContext):
    await state.set_state(Func1.choose_option)
    await profile_start(message, state)

