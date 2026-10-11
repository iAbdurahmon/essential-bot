from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, User
from lg_messages.func import lg_check, lg_check3


def language_selection(items: list[str]) -> ReplyKeyboardMarkup:
    row1 = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row1], resize_keyboard=True)


def row1(items: list[str]) -> ReplyKeyboardMarkup:
    row1 = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row1], resize_keyboard=True)


def main_buttons(items: list[str], message: Message) -> ReplyKeyboardMarkup:
    mid = len(items) // 2
    row1 = [KeyboardButton(text=item) for item in items[:mid]]
    row2 = [KeyboardButton(text=item) for item in items[mid:]]

    keyboard = ReplyKeyboardMarkup(keyboard=[row1, row2],
                                   resize_keyboard=True,
                                   input_field_placeholder=lg_check('Select an option',
                                                                    'Выберите вариант',
                                                                    'Variantni tanlang', message)
                                   )

    return keyboard


def func_kb(items: list[str], message: Message) -> ReplyKeyboardMarkup:
    if len(items) % 2 == 1:  # doesn't divisible by two
        mid = (len(items) - 1) // 2
        row1 = [KeyboardButton(text=item) for item in items[:mid]]
        row2 = [KeyboardButton(text=item) for item in items[mid:-1]]
        row3 = [KeyboardButton(text=items[-1])]

        keyboard = ReplyKeyboardMarkup(keyboard=[row1, row2, row3],
                                       resize_keyboard=True,
                                       input_field_placeholder=lg_check(
                                           'Select an option',
                                           'Выберите вариант',
                                           'Variantni tanlang', message)
                                       )

        return keyboard
    elif len(items) % 2 == 0:  # divisible by two with one time keyboard
        mid = (len(items) - 2) // 2
        row1 = [KeyboardButton(text=item) for item in items[:mid]]
        row2 = [KeyboardButton(text=item) for item in items[mid:-2]]
        row3 = [KeyboardButton(text=item) for item in items[-2:]]

        keyboard = ReplyKeyboardMarkup(keyboard=[row1, row2, row3],
                                       resize_keyboard=True,
                                       input_field_placeholder=lg_check(
                                           'Select an option',
                                           'Выберите вариант',
                                           'Variantni tanlang', message)
                                       )

        return keyboard


def func_kb2(items: list[str], from_user: User) -> ReplyKeyboardMarkup:
    if len(items) % 2 == 1:  # doesn't divisible by two
        mid = (len(items) - 1) // 2
        row1 = [KeyboardButton(text=item) for item in items[:mid]]
        row2 = [KeyboardButton(text=item) for item in items[mid:-1]]
        row3 = [KeyboardButton(text=items[-1])]

        keyboard = ReplyKeyboardMarkup(keyboard=[row1, row2, row3],
                                       resize_keyboard=True,
                                       input_field_placeholder=lg_check3(
                                           'Select an option',
                                           'Выберите вариант',
                                           'Variantni tanlang', from_user)
                                       )

        return keyboard
    elif len(items) % 2 == 0:  # divisible by two with one time keyboard
        mid = (len(items) - 2) // 2
        row1 = [KeyboardButton(text=item) for item in items[:mid]]
        row2 = [KeyboardButton(text=item) for item in items[mid:-2]]
        row3 = [KeyboardButton(text=item) for item in items[-2:]]

        keyboard = ReplyKeyboardMarkup(keyboard=[row1, row2, row3],
                                       resize_keyboard=True,
                                       input_field_placeholder=lg_check3(
                                           'Select an option',
                                           'Выберите вариант',
                                           'Variantni tanlang', from_user)
                                       )

        return keyboard


def buttons3(items: list[str], message: Message) -> ReplyKeyboardMarkup:
    thr = len(items) // 3 + len(items) // 3
    row1 = [KeyboardButton(text=item) for item in items[:thr]]
    row2 = [KeyboardButton(text=item) for item in items[thr:]]

    keyboard = ReplyKeyboardMarkup(keyboard=[row1, row2],
                                   resize_keyboard=True,
                                   input_field_placeholder=lg_check(
                                       'Select an option',
                                       'Выберите вариант',
                                       'Variantni tanlang', message)
                                   )
    return keyboard


def buttons3_custom_no_message(items: list[str]) -> ReplyKeyboardMarkup:
    row1 = [KeyboardButton(text=item) for item in items[:1]]
    row2 = [KeyboardButton(text=item) for item in items[1:]]

    keyboard = ReplyKeyboardMarkup(keyboard=[row1, row2],
                                   resize_keyboard=True
                                   )

    return keyboard


def buttons4_2(items: list[str], message: Message) -> ReplyKeyboardMarkup: # 2-1
    row1 = [KeyboardButton(text=item) for item in items[:3]]
    row2 = [KeyboardButton(text=items[3])]
    row3 = [KeyboardButton(text=item) for item in items[4:]]

    keyboard = ReplyKeyboardMarkup(keyboard=[row1, row2, row3],
                                   resize_keyboard=True,
                                   input_field_placeholder=lg_check(
                                       'Select an option',
                                       'Выберите вариант',
                                       'Variantni tanlang', message)
                                   )
    return keyboard


def custom_1_3_2(items: list[str]) -> ReplyKeyboardMarkup:
    row1 = [KeyboardButton(text=item) for item in items[:1]]
    row2 = [KeyboardButton(text=item) for item in items[1:4]]
    row3 = [KeyboardButton(text=item) for item in items[4:]]

    keyboard = ReplyKeyboardMarkup(keyboard=[row1, row2, row3],
                                   resize_keyboard=True
                                   )

    return keyboard

def custom_5(items: list[str]) -> ReplyKeyboardMarkup:
    row1 = [KeyboardButton(text=item) for item in items[:3]]
    row2 = [KeyboardButton(text=item) for item in items[3:]]

    keyboard = ReplyKeyboardMarkup(keyboard=[row1, row2],
                                   resize_keyboard=True
                                   )

    return keyboard
