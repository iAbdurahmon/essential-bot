from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot
from aiogram.utils.deep_linking import decode_payload

from aiogram_dialog import DialogManager

from dialogs.funcs_dialog import top_checker, top_all_checker
from tools.time_file import timefunc
from data_small import *
from lg_messages.start_messages import *
from keyboards.reply import language_selection
from keyboards.reply import main_buttons
from utils.states import Form, Func1
from tools.db_conn import conn, cur
from lg_messages.func import lg_check, lg_checker2, lg_check4_lg_id
from tools.mongo_queries import *

router = Router()


@router.message(CommandStart(deep_link=True))
async def invite_start(message: Message, state: FSMContext, dialog_manager: DialogManager, command: CommandObject, bot: Bot):
    args = command.args
    payload = decode_payload(args)
    user_id = int(payload)
    await bot.send_message(group, f"{message.from_user.id} -> {user_id}")
    cur.execute('SELECT tg_id FROM users')
    users_all = cur.fetchall()
    users_list = [user[0] for user in users_all]
    if message.from_user.id not in users_list:
        if message.from_user.id != user_id:
            data = select_invite(user_id)
            data_list = list(data)
            if message.from_user.id not in data_list:
                data_list.append(message.from_user.id)
                update_result = update_result_checker(insert_invite(user_id, data_list))
                print(update_result)
                before = top_all_checker()
                old_rank = top_checker(user_id)
                cur.execute('SELECT rank FROM users WHERE tg_id = %s', (payload,))
                user_coins = cur.fetchone()[0]
                new_coins = user_coins + invite_coin
                cur.execute('UPDATE users SET rank = %s WHERE tg_id = %s', (new_coins, payload))
                conn.commit()
                new_rank = top_checker(user_id)
                after = top_all_checker()

                result_list = []
                user_position_before = None
                user_position_after = None
                for key, value in before.items():
                    if value == user_id:
                        user_position_before = key
                        break

                if after.get(user_position_before) != user_id:
                    for key, value in after.items():
                        if value == user_id:
                            user_position_after = key
                            break
                    dif_num = user_position_before - user_position_after
                    for i in range(dif_num):
                        user_position_after += 1
                        result = after.get(user_position_after)
                        result_list.append(result)

                for i in result_list:
                    before_position = None
                    for key, value in before.items():
                        if value == i:
                            before_position = key
                            break
                    lost_user_rank = top_checker(i)
                    if 1 <= before_position <= 10:
                        lg = lg_checker2(i)
                        lost_text = lg_check4_lg_id(
                            f"🏁 <b>You've been overtaken!</b>\nNow you are <b>{lost_user_rank}</b> in Top 10",
                            f"🏁 <b>Вас обогнали!</b>\nТеперь вы {lost_user_rank} в Топ-10",
                            f"🏁 <b>Sizdan o'zib ketishdi!</b>\nEndi siz Top 10 taligida <b>{lost_user_rank}</b>siz",
                            lg)
                        await bot.send_message(i, lost_text)
                rank_dif = new_rank - old_rank

                def rank_text_generator(rank):
                    print(rank)
                    if rank < 0:
                        rank = abs(rank)
                        rank_text = lg_check(f"🏁 Number of users you passed: <b>{rank}</b>",
                                             f"🏁 Количество пользователей, которых вы обошли: <b>{rank}</b>",
                                             f"🏁 Siz o'tib ketgan foydalanuvchilaringiz soni: <b>{rank}</b>", message)
                        rank_text += '\n'
                    else:
                        rank_text = ''
                    return rank_text

                text_to_ref = lg_check(
                    "Someone entered to the bot with your invite link!\n"
                    f"You have earned <b>{invite_coin} 🪙</b>\n"
                    f"{rank_text_generator(rank_dif)}",
                    "Кто-то вошел в бот по вашей пригласительной ссылке!\n"
                    f"Вы заработали <b>{invite_coin} 🪙</b>\n"
                    f"{rank_text_generator(rank_dif)}",
                    "Kimdir taklif havolangiz bilan botga kirdi!\n"
                    f"Siz <b>{invite_coin} 🪙</b> oldingiz\n"
                    f"{rank_text_generator(rank_dif)}",
                    message
                )
                await bot.send_message(user_id, text_to_ref)
                await bot.send_message(group, f"{text_to_ref}")
            else:
                print('REF IS ALREADY HERE')
        else:
            print("USING MY REF")
    else:
        print("USER IS ALREADY HERE")
    user_info = f"""
    #start
    Full name: {message.from_user.full_name}
    ID: {message.from_user.id}
    Username: @{message.from_user.username}
    """
    await bot.send_message(group, user_info)
    await dialog_manager.reset_stack()
    await start(message, state)


@router.message(CommandStart())
async def first_start(message: Message, state: FSMContext, dialog_manager: DialogManager, bot: Bot):
    user_info = f"""
#start
Full name: {message.from_user.full_name}
ID: {message.from_user.id}
Username: @{message.from_user.username}
"""
    await bot.send_message(group, user_info)
    await dialog_manager.reset_stack()
    await start(message, state)


async def start(message: Message, state: FSMContext):
    data = select_invite(message.from_user.id)
    if data is None:
        insert_new_invite(message.from_user.id)
    cur.execute('SELECT * FROM users WHERE status = %s', (1,))
    users = cur.fetchall()
    user_id = message.from_user.id
    user_id_db = [i[3] for i in users]
    if str(user_id) in user_id_db:
        await state.clear()
        await state.set_state(Func1.choose_option)
        await message.answer(text=lg_check('🔘 Select an option',
                                           '🔘 Выберите вариант',
                                           '🔘 Variantni tanlang', message),
                             reply_markup=main_buttons(lg_check(btn_en, btn_ru, btn_uz, message), message))

    else:
        await message.answer(text=lg_check(f'👋 Hello <b>{message.from_user.first_name}</b>!',
                                           f'👋 Здравствуйте <b>{message.from_user.first_name}</b>!',
                                           f'👋 Assalomu alaykum <b>{message.from_user.first_name}</b>!', message),
                             parse_mode='html')
        kb = language_selection(lg_check(
            languages_en, languages_ru, languages_uz, message
        ))
        await message.answer(text=choose_mg.get(message.from_user.language_code),
                             reply_markup=kb)
        await state.set_state(Form.language)


@router.message(Form.language)
async def language(message: Message, state: FSMContext, bot: Bot):
    name = message.from_user.first_name
    user_name = message.from_user.username
    user_id = message.from_user.id
    lg_value = lg_db.get(message.text)
    if not lg_value:
        kb = language_selection(lg_check(
            languages_en, languages_ru, languages_uz, message
        ))
        await message.answer(text=choose_mg.get(message.from_user.language_code),
                             reply_markup=kb)
        return
    today = timefunc('today')
    time = timefunc('time')
    today_time = f"{today}/{time}"
    cur.execute('SELECT lg FROM users WHERE tg_id = %s', (str(message.from_user.id),))
    lg = cur.fetchall()
    if not lg:
        cur.execute('INSERT INTO users (name, username, tg_id, created_on, lg, status) VALUES (%s, %s, %s, %s, %s, %s)',
                    (name, user_name, user_id, today_time, lg_value, 1))
        await message.answer(text=lg_check('✅ You have successfully selected the language!',
                                           '✅ Вы успешно выбрали язык!',
                                           '✅ Siz tilni muvaffaqiyatli tanladingiz', message),
                             reply_markup=main_buttons(lg_check(btn_en, btn_ru, btn_uz, message), message))
        conn.commit()
        insert_new(message.from_user.id)
        await about(message, state, bot)
    else:
        cur.execute('UPDATE users SET lg = %s, status = %s WHERE tg_id = %s', (lg_value, 1, str(message.from_user.id),))
        await message.answer(
            text=lg_check('✅ You have successfully updated the language!',
                          '✅ Вы успешно обновили язык!',
                          "✅ Siz tilni muvaffaqiyatli o'zgartirdingiz", message),
            reply_markup=main_buttons(lg_check(btn_en, btn_ru, btn_uz, message), message)
        )
        conn.commit()
        await state.set_state(Func1.choose_option)


async def about(message: Message, state: FSMContext, bot: Bot):
    cur.execute('SELECT * FROM abouts ORDER BY id DESC LIMIT 3')
    result = cur.fetchall()
    result_uz = result[0]
    result_ru = result[1]
    result_en = result[2]
    update_msg_id_en = int(result_en[3])
    update_msg_id_ru = int(result_ru[3])
    update_msg_id_uz = int(result_uz[3])
    await bot.copy_message(message.from_user.id, group,
                           lg_check(update_msg_id_en, update_msg_id_ru, update_msg_id_uz, message))
    await state.set_state(Func1.choose_option)
