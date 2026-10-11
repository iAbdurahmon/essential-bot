from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

UNITS_IN_BOOK = 30


def units_inline(book: str, back_text: str, width: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for unit in range(1, UNITS_IN_BOOK + 1):
        builder.button(text=str(unit), callback_data=f"wl:{book}:{unit}")
    builder.adjust(width)
    builder.row(InlineKeyboardButton(text=back_text, callback_data='wl:back'))
    return builder.as_markup()
