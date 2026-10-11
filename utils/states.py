from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    language = State()
    about = State()
    main_button = State()
    word_list = State()
    # many doesn't work state


class Func1(StatesGroup):
    choose_option = State()
    choose_book_or_list = State()
    choose_book = State()


class Books(StatesGroup):
    books = State()


class Poll_state(StatesGroup):
    dialog_start = State()
    dialog_started = State()


class Translate(StatesGroup):
    from_lg = State()
    to_lg = State()
    text = State()


class Profile(StatesGroup):
    profile_start = State()
    rating = State()


class Status(StatesGroup):
    on = State()
