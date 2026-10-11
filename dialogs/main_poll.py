import random
import time

from typing import Any
from collections import Counter
from dataclasses import dataclass, field

from aiogram import Bot
from aiogram import Router, F
from aiogram.fsm.scene import Scene, on
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PollAnswer
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tools.db_conn import cur, conn
from tools.mongo_queries import update_coins, select_coin, update_result_checker
from data_small import *
from lg_messages.func import lg_check, lg_check2, lg_check4_lg_id, lg_checker2
from keyboards.reply import row1
from dialogs.funcs_dialog import top_checker, top_all_checker

router_poll = Router()


@dataclass
class Answer:
    text: str
    is_correct: bool = False


@dataclass
class Question:
    text: str
    answers: list[Answer]
    correct_answer_id: int = field(init=True)
    correct_answer: str = field(init=True)

    chat_id: int = field(init=False)


def data_setup(from_lg, to_lg, message: Message):
    ques = []
    option_ids = []
    QUESTIONS = []
    data_all = []
    data = user_data.get(message.from_user.id)
    book = data.get('book')
    unit_selected = data.get('units')

    for unit in unit_selected:
        cur.execute(f"SELECT id, {from_lg}, {to_lg} FROM book{book} WHERE unit=%s", (unit,))
        data_base = cur.fetchall()
        data_all.append(data_base)
    for i in data_all:
        for obj in i:
            correct_answer = obj[2]
            options = []

            while len(options) < 3:
                sample = random.sample([w[2] for w in i if w[2] != correct_answer], 3)
                sample_original = sample.copy()
                for idx in range(len(sample)):
                    sample[idx] = sample[idx].strip()
                if len(set(sample)) == 3 and correct_answer.strip() not in sample:
                    options = sample_original
                else:
                    print('DIMOOON')
                    print(sample)

            options.insert(0, correct_answer)
            print(options)
            questions = Question(
                text=obj[1],
                answers=[Answer(text=answer, is_correct=(idx == 0)) for idx, answer in enumerate(options)],
                correct_answer_id=0,
                correct_answer=''
            )
            QUESTIONS.append(questions)

            option_id = {idx: option for idx, option in enumerate(options)}
            option_ids.append(option_id)

            ques.append(obj[1])

    data['questions'] = QUESTIONS
    data['option_ids'] = option_ids
    data['ques'] = ques


class QuizScene(Scene, state="quiz"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, step: int | None = 0) -> Any:
        data = user_data.get(message.from_user.id)
        checked_from = data.get('from')
        checked_to = data.get('to')
        from_lg = lg_reductions.get(checked_from)
        to_lg = lg_reductions.get(checked_to)
        data_setup(from_lg, to_lg, message)

        QUESTIONS = data.get('questions')
        option_ids = data.get('option_ids')
        ques = data.get('ques')
        ques_id = []
        index_of_random_answers = []

        random.shuffle(QUESTIONS)
        try:
            quiz = QUESTIONS[step]
            random.shuffle(quiz.answers)
            for idx, answer in enumerate(quiz.answers):
                if answer.is_correct:
                    quiz.correct_answer_id = idx
                    quiz.correct_answer = answer.text
                    break

        except IndexError:
            return await self.wizard.exit()

        idx2 = None
        for idx, i_new in enumerate(ques):
            if i_new == quiz.text:
                idx2 = idx
                break

        ques_id.append(idx2)

        result = [option_ids[idx2].get(j, None) for j in range(4)]
        for i2_new in quiz.answers:
            if i2_new.text in result:
                index_in_result = result.index(i2_new.text)
                index_of_random_answers.append(index_in_result)

        markup = ReplyKeyboardBuilder()
        stop_button = await lg_check2("Stop", "Остановить", "To'xtatish", message.from_user)
        next_button = await lg_check2("Next", "Пропустить", "Kengisi", message.from_user)
        markup.button(text=f"🚫 {stop_button}")
        markup.button(text=f"➡️ {next_button}")

        data['questions'] = QUESTIONS
        data['start_time'] = time.time()
        data['ques_id'] = ques_id
        data['index_of_random_answers'] = index_of_random_answers
        step_text = step + 1

        await state.update_data(step=step)
        return await message.answer_poll(
            question=f"{step_text}. {QUESTIONS[step].text}",
            options=[answer.text for answer in quiz.answers],
            correct_option_id=quiz.correct_answer_id,
            is_anonymous=False,
            type='quiz',
            open_period=30,
            reply_markup=markup.adjust(2).as_markup(resize_keyboard=True)
        )

    @on.poll_answer.enter()
    async def on_enter2(self, message: PollAnswer, bot: Bot, state: FSMContext, step: int | None = 0) -> Any:
        try:
            data = user_data.get(message.user.id)
            QUESTIONS = data.get('questions')
            option_ids = data.get('option_ids')
            ques = data.get('ques')
            ques_id = data.get('ques_id')
            index_of_random_answers = data.get('index_of_random_answers')
            quiz = QUESTIONS[step]
            random.shuffle(quiz.answers)
            for idx, answer in enumerate(quiz.answers):
                if answer.is_correct:
                    quiz.correct_answer_id = idx
                    quiz.correct_answer = answer.text
                    break
        except IndexError:
            return await self.wizard.exit()

        idx2 = None
        for idx, i in enumerate(ques):
            if i == quiz.text:
                idx2 = idx
                break

        ques_id[0] = idx2

        result = [option_ids[idx2].get(j, None) for j in range(4)]
        for i2 in quiz.answers:
            if i2.text in result:
                index_in_result = result.index(i2.text)
                index_of_random_answers.append(index_in_result)

        markup = ReplyKeyboardBuilder()
        stop_button = await lg_check2("Stop", "Остановить", "To'xtatish", message.user)
        next_button = await lg_check2("Next", "Пропустить", "Kengisi", message.user)
        markup.button(text=f"🚫 {stop_button}")
        markup.button(text=f"➡️ {next_button}")

        data['questions'] = QUESTIONS
        data['ques_id'] = ques_id
        data['index_of_random_answers'] = index_of_random_answers

        await state.update_data(step=step)

        step_text = step + 1
        return await bot.send_poll(
            chat_id=message.user.id,
            question=f"{step_text}. {QUESTIONS[step].text}",
            options=[answer.text for answer in quiz.answers],
            correct_option_id=quiz.correct_answer_id,
            is_anonymous=False,
            type='quiz',
            open_period=30,
            reply_markup=markup.adjust(2).as_markup(resize_keyboard=True))

    @on.message(F.text.in_(["➡️ Next", "➡️ Пропустить", "➡️ Kengisi"]))
    async def on_enter3(self, message: Message, bot: Bot, state: FSMContext) -> Any:
        data = await state.get_data()
        step = data["step"] + 1
        try:
            wrem = user_data.get(message.from_user.id)
            QUESTIONS = wrem.get('questions')
            option_ids = wrem.get('option_ids')
            ques = wrem.get('ques')
            ques_id = wrem.get('ques_id')
            index_of_random_answers = wrem.get('index_of_random_answers')
            quiz = QUESTIONS[step]
            random.shuffle(quiz.answers)

            index_of_random_answers.clear()
            for idx, answer in enumerate(quiz.answers):
                if answer.is_correct:
                    quiz.correct_answer_id = idx
                    quiz.correct_answer = answer.text
                    break
        except IndexError:
            return await self.wizard.exit()

        idx2 = None
        for idx, i in enumerate(ques):
            if i == quiz.text:
                idx2 = idx
                break

        ques_id[0] = idx2

        result = [option_ids[idx2].get(j, None) for j in range(4)]
        for i2 in quiz.answers:
            if i2.text in result:
                index_in_result = result.index(i2.text)
                index_of_random_answers.append(index_in_result)

        markup = ReplyKeyboardBuilder()
        stop_button = await lg_check2("Stop", "Остановить", "To'xtatish", message.from_user)
        next_button = await lg_check2("Next", "Пропустить", "Kengisi", message.from_user)
        markup.button(text=f"🚫 {stop_button}")
        markup.button(text=f"➡️ {next_button}")

        wrem['questions'] = QUESTIONS
        wrem['ques_id'] = ques_id
        wrem['index_of_random_answers'] = index_of_random_answers

        step_text = step + 1

        await state.update_data(step=step)
        return await message.answer_poll(
            question=f"{step_text}. {QUESTIONS[step].text}",
            options=[answer.text for answer in quiz.answers],
            correct_option_id=quiz.correct_answer_id,
            is_anonymous=False,
            type='quiz',
            open_period=30,
            reply_markup=markup.adjust(2).as_markup(resize_keyboard=True)
        )

    @on.message.exit()
    async def on_exit(self, message: Message, bot: Bot, state: FSMContext) -> None:
        data = await state.get_data()
        answers = data.get("answers", {})
        step2 = data['step']

        wrem = user_data.get(message.from_user.id)
        QUESTIONS = wrem['questions']
        book = wrem['book']
        units = wrem['units']

        correct_answers = []
        correct_answers_org = []

        correct_answers_mis = []
        correct_answers_org_mis = []

        correct = 0
        incorrect = 0
        missed = 0
        total = 0
        correct_units = []
        for step, quiz in enumerate(QUESTIONS):
            answer = answers.get(str(step))
            if answer == quiz.correct_answer:
                correct += 1
                cur.execute(f"""
                                SELECT unit
                                FROM book{book}
                                WHERE eng = %s
                                   OR rus = %s
                                   OR uzb = %s;
                            """, (answer, answer, answer))
                units_answer = cur.fetchone()
                for i in units_answer:
                    correct_units.append(i)
            elif answer is None:
                correct_answers_mis.append(quiz.correct_answer)
                correct_answers_org_mis.append(quiz.text)
                missed += 1
            elif answer != quiz.correct_answer:
                correct_answers.append(quiz.correct_answer)
                correct_answers_org.append(quiz.text)
                incorrect += 1
            if step == step2:
                break

        for qty, i in enumerate(QUESTIONS):
            total = qty + 1

        try:
            pre_percentage = total / correct
            percentage = 100 / pre_percentage
            per_round = round(percentage, 1)
        except ZeroDivisionError:
            per_round = 0
        coins = correct * 2

        unit_counts = Counter(correct_units)
        unit_count_dict = dict(unit_counts)
        user_coins_unit = {}
        for unit in unit_count_dict.keys():
            result = update_result_checker(select_coin(message.from_user.id, book, unit))
            print(result)
            if isinstance(result, int):
                user_coins_unit[unit] = result
            else:
                user_coins_unit[unit] = 0
                await bot.send_message(group,
                                       f"ERROR ZERO: {message.from_user.first_name} - {message.from_user.id} - @{message.from_user.username}")

        old_coins = sum(user_coins_unit.values())
        new_coins = coins

        try:
            pre_percentage_old = total * 2 / old_coins
            percentage_old = 100 / pre_percentage_old
        except ZeroDivisionError:
            percentage_old = 0

        try:
            pre_percentage_new = total * 2 / new_coins
            percentage_new = 100 / pre_percentage_new
        except ZeroDivisionError:
            percentage_new = 0

        progress = percentage_new - percentage_old
        progress = round(progress, 1)

        if progress > 0:
            for mongo_unit in unit_count_dict.keys():
                coins2 = unit_count_dict.get(mongo_unit) * 2
                result = update_result_checker(update_coins(message.from_user.id, book, mongo_unit, coins2))
                print(result)
        else:
            new_coins = old_coins

        old_rank = top_checker(message.from_user.id)
        before = top_all_checker()

        cur.execute('SELECT rank FROM users WHERE tg_id = %s', (f"{message.from_user.id}",))
        user_coins = cur.fetchone()[0]
        if user_coins is None:
            user_coins = 0
        coins_different = new_coins - old_coins
        all_coins = user_coins + coins_different
        cur.execute('UPDATE users SET rank = %s WHERE tg_id = %s', (all_coins, f"{message.from_user.id}"))
        conn.commit()

        new_rank = top_checker(message.from_user.id)
        after = top_all_checker()

        user_id = message.from_user.id
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

        pre_text1 = lg_check('Your results', 'Ваши результаты', 'Sizning natijalaringiz', message)
        pre_text2 = lg_check('Total questions', 'Всего вопросов', 'Jami savollar', message)
        pre_text2_5 = lg_check('Percentage', 'Процент', 'Foiz', message)
        pre_text2_6 = lg_check('Progress', 'Прогресс', 'Progres', message)
        pre_text3 = lg_check('Correct', 'Правильные', 'Tog\'ri', message)
        pre_text4 = lg_check('Incorrect', 'Неправильные', 'Noto\'g\'ri', message)
        pre_text5 = lg_check('Missed', 'Пропущенные', 'O\'tkazib yuborilgan', message)
        pre_text6 = lg_check('Your incorrect answers:', 'Ваши неправильные ответы:',
                             'Sizning noto\'g\'ri javoblaringiz:',
                             message)
        pre_text7 = lg_check("Use a bot to learn new words: @essentialwordstestbot",
                             "Используйте бота для изучения новых слов: @essentialwordstestbot",
                             "Yangi so'zlarni o'rganish uchun botdan foydalaning: @essentialwordstestbot", message)

        pre_text_hour1 = lg_check('hour', 'час', 'soat', message)
        pre_text_hour2 = lg_check('hours', 'часа', 'soat', message)
        pre_text_hour3 = lg_check('hours', 'часов', 'soat', message)
        pre_text_min1 = lg_check('minute', 'минута', 'daqiqa', message)
        pre_text_min2 = lg_check('minutes', 'минуты', 'daqiqa', message)
        pre_text_min3 = lg_check('minutes', 'минут', 'daqiqa', message)
        pre_text_sec1 = lg_check('second', 'секунда', 'soniya', message)
        pre_text_sec2 = lg_check('seconds', 'секунды', 'soniya', message)
        pre_text_sec3 = lg_check('seconds', 'секунд', 'soniya', message)

        start_time = wrem.get('start_time')
        time_now = time.time()
        elapsed_time = time_now - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)

        def time_formatter():
            if hours == 1:
                hours_text = f"1 {pre_text_hour1} "
            elif 2 <= hours < 5:
                hours_text = f"{hours} {pre_text_hour2} "
            else:
                hours_text = f"{hours} {pre_text_hour3} "
            if hours == 0:
                hours_text = ''

            if minutes == 1:
                minutes_text = f"1 {pre_text_min1}  "
            elif 2 <= hours < 5:
                minutes_text = f"{minutes} {pre_text_min2} "
            else:
                minutes_text = f"{minutes} {pre_text_min3} "
            if minutes == 0:
                minutes_text = ''

            if seconds == 1:
                seconds_text = f"1 {pre_text_sec1} "
            elif 2 <= hours < 5:
                seconds_text = f"{seconds} {pre_text_sec2} "
            else:
                seconds_text = f"{seconds} {pre_text_sec3} "
            if seconds == 0:
                seconds_text = ''
            return hours_text + minutes_text + seconds_text

        def correct_answers_org_var_func(key):
            if key == 'inc':
                if correct_answers_org:
                    correct_answers_org_var = ''
                    for num, (a, b) in enumerate(zip(correct_answers_org, correct_answers), 1):
                        correct_answers_org_var += f'`{num}. {a} -- {b}`\n'
                    correct_answers_org_var += '\n'
                    return correct_answers_org_var
            else:
                if correct_answers_mis:
                    correct_answers_org_var_mis = ''
                    for num, (a, b) in enumerate(zip(correct_answers_org_mis, correct_answers_mis), 1):
                        correct_answers_org_var_mis += f'`{num}. {a} -- {b}`\n'
                    return correct_answers_org_var_mis
            return ''

        def is_zero(key_zero):
            if key_zero == 'inc':
                if incorrect != 0:
                    return f'{pre_text6}\n'
            elif key_zero == 'mis':
                if missed != 0:
                    return pre_text5
            return ''

        def progress_is_good(progress_value):
            if progress > 0:
                return f'🔺 {progress_value}'
            elif progress == 0:
                return f'{progress_value}'
            else:
                return f'🔻 {progress_value}'

        def emoji_is_good(progress_emoji):
            if progress_emoji > 0:
                return '📈'
            else:
                return '📉'

        hashtag_text = ''
        for i in units:
            hashtag_text += f'#u{i} '

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

        pre_text = (f"📈 *{pre_text1}:*\n"  # Your results
                    f"#Book{book}\n"  # hashtags
                    f"🖇️ _Units:_ {hashtag_text}\n\n"  # hashtags

                    f"❓ _{pre_text2}:_ *{total}*\n"  # Total questions
                    f"💯 _{pre_text2_5}:_ *{per_round}%*\n"  # Percentage
                    f"{emoji_is_good(progress)} _{pre_text2_6}:_ *{progress_is_good(progress)}%*\n"  # Progress
                    f"☑️ _{pre_text3}:_ *{correct}*\n"  # Correct
                    f"❌ _{pre_text4}:_ *{incorrect}*\n"  # Incorrect
                    f"🔄 _{pre_text5}:_ *{missed}*\n"  # Missed
                    f"⌛️ *{time_formatter()}*\n"  # timer
                    '\n'
                    f"*{is_zero('inc')}*"  # Your incorrect answers
                    f"{correct_answers_org_var_func('inc')}"  # list ^

                    f"*{is_zero('mis')}*\n"  # Your missed answers
                    f"{correct_answers_org_var_func('mis')}\n"  # list ^\
                    f"🤖 {pre_text7}"
                    )

        if coins_different > 0:
            coin_text_en = (f"<b>You have earned {coins_different} 🪙</b>\n\n"
                            f"<i>💰 Your balance: {all_coins} 🪙</i>\n"
                            f"<i>{rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Your place in Top 10: /top10</i>")

            coin_text_ru = (f"<b>Вы получили {coins_different} 🪙</b>\n\n"
                            f"<i>💰 Ваш баланс: {all_coins} 🪙</i>\n"
                            f"<i>{rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Ваше место в Топ-10: /top10</i>")

            coin_text_uz = (f"<b>Siz {coins_different} 🪙 oldingiz</b>\n\n"
                            f"<i>💰 Balansingiz: {all_coins} 🪙</i>\n"
                            f"<i>{rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Top 10 dagi joyingiz: /top10</i>")
        else:
            coin_text_en = (f"<b>You couldn't get 🪙, improve your progress!</b>\n\n"
                            f"<i>💰 Your balance: {all_coins} 🪙</i>\n"
                            f"<i>{rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Your place in Top 10: /top10</i>")

            coin_text_ru = (f"<b>вы не смогли получить 🪙, улучшайте прогресс!</b>\n\n"
                            f"<i>💰 Ваш баланс: {all_coins} 🪙</i>\n"
                            f"<i>{rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Ваше место в Топ-10: /top10</i>")

            coin_text_uz = (f"<b>siz 🪙 ololmadingiz, progresni oshiring!</b>\n\n"
                            f"<i>💰 Balansingiz: {all_coins} 🪙</i>\n"
                            f"<i>{rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Top 10 dagi joyingiz: /top10</i>")
        coin_text = lg_check(coin_text_en, coin_text_ru, coin_text_uz, message)

        await message.answer(pre_text, reply_markup=row1([lg_check("🏠 Main Menu", "🏠 Главное Меню",
                                                                   "🏠 Asosiy Menyu", message)]),
                             parse_mode="MARKDOWN")
        await message.answer(coin_text)
        pre_text_admin = f"#quiz\n{coin_text}\n{message.from_user.first_name} - {message.from_user.id} - @{message.from_user.username}"
        await bot.send_message(group, pre_text_admin)
        await bot.send_message(group, pre_text, parse_mode="MARKDOWN")
        await state.clear()

    @on.poll_answer.exit()
    async def on_exit2(self, message: PollAnswer, bot: Bot, state: FSMContext) -> None:
        data = await state.get_data()
        answers = data.get("answers", {})
        step2 = data['step']

        data_all = user_data[message.user.id]
        QUESTIONS = data_all['questions']
        book = data_all['book']
        units = data_all['units']

        correct_answers = []
        correct_answers_org = []

        correct_answers_mis = []
        correct_answers_org_mis = []

        correct = 0
        incorrect = 0
        missed = 0
        total = 0
        correct_units = []
        for step, quiz in enumerate(QUESTIONS):
            answer = answers.get(str(step))
            if answer == quiz.correct_answer:
                correct += 1
                cur.execute(f"""
                                SELECT unit
                                FROM book{book}
                                WHERE eng = %s
                                   OR rus = %s
                                   OR uzb = %s;
                            """, (answer, answer, answer))
                units_answer = cur.fetchone()
                for i in units_answer:
                    correct_units.append(i)
            elif answer is None:
                correct_answers_mis.append(quiz.correct_answer)
                correct_answers_org_mis.append(quiz.text)
                missed += 1
            elif answer != quiz.correct_answer:
                correct_answers.append(quiz.correct_answer)
                correct_answers_org.append(quiz.text)
                incorrect += 1
            if step == step2:
                break

        for qty, i in enumerate(QUESTIONS):
            total = qty + 1

        try:
            pre_percentage = total / correct
            percentage = 100 / pre_percentage
            per_round = round(percentage, 1)
        except ZeroDivisionError:
            per_round = 0

        coins = correct * 2

        unit_counts = Counter(correct_units)
        unit_count_dict = dict(unit_counts)
        user_coins_unit = {}
        for unit in unit_count_dict.keys():
            result = update_result_checker(select_coin(message.user.id, book, unit))
            if isinstance(result, int):
                user_coins_unit[unit] = result
            else:
                user_coins_unit[unit] = 0
                await bot.send_message(group,
                                       f"ERROR ZERO: {message.user.first_name} - {message.user.id} - @{message.user.username}")

        old_coins = sum(user_coins_unit.values())
        new_coins = coins

        try:
            pre_percentage_old = total * 2 / old_coins
            percentage_old = 100 / pre_percentage_old
        except ZeroDivisionError:
            percentage_old = 0

        try:
            pre_percentage_new = total * 2 / new_coins
            percentage_new = 100 / pre_percentage_new
        except ZeroDivisionError:
            percentage_new = 0

        progress = percentage_new - percentage_old
        progress = round(progress, 1)

        if progress > 0:
            for mongo_unit in unit_count_dict.keys():
                coins2 = unit_count_dict.get(mongo_unit) * 2
                result = update_result_checker(update_coins(message.user.id, book, mongo_unit, coins2))
                print(result)
        else:
            new_coins = old_coins

        old_rank = top_checker(message.user.id)
        before = top_all_checker()

        cur.execute('SELECT rank FROM users WHERE tg_id = %s', (f"{message.user.id}",))
        user_coins = cur.fetchone()[0]
        if user_coins is None:
            user_coins = 0
        coins_different = new_coins - old_coins
        all_coins = user_coins + coins_different
        cur.execute('UPDATE users SET rank = %s WHERE tg_id = %s', (all_coins, f"{message.user.id}"))
        conn.commit()

        new_rank = top_checker(message.user.id)
        after = top_all_checker()

        user_id = message.user.id
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

        pre_text1 = await lg_check2('Your results', 'Ваши результаты', 'Sizning natijalaringiz', message.user)
        pre_text2 = await lg_check2('Total questions', 'Всего вопросов', 'Jami savollar', message.user)
        pre_text2_5 = await lg_check2('Percentage', 'Процент', 'Foiz', message.user)
        pre_text2_6 = await lg_check2('Progress', 'Прогресс', 'Progres', message.user)
        pre_text3 = await lg_check2('Correct', 'Правильные', 'Tog\'ri', message.user)
        pre_text4 = await lg_check2('Incorrect', 'Неправильные', 'Noto\'g\'ri', message.user)
        pre_text5 = await lg_check2('Missed', 'Пропущенные', 'O\'tkazib yuborilgan', message.user)
        pre_text6 = await lg_check2('Your incorrect answers', 'Ваши неправильные ответы',
                                    'Sizning noto\'g\'ri javoblaringiz',
                                    message.user)
        pre_text7 = await lg_check2("Use a bot to learn new words: @essentialwordstestbot",
                                    "Используйте бота для изучения новых слов: @essentialwordstestbot",
                                    "Yangi so'zlarni o'rganish uchun botdan foydalaning: @essentialwordstestbot",
                                    message.user)

        pre_text_hour1 = await lg_check2('hour', 'час', 'soat', message.user)
        pre_text_hour2 = await lg_check2('hours', 'часа', 'soat', message.user)
        pre_text_hour3 = await lg_check2('hours', 'часов', 'soat', message.user)
        pre_text_min1 = await lg_check2('minute', 'минута', 'daqiqa', message.user)
        pre_text_min2 = await lg_check2('minutes', 'минуты', 'daqiqa', message.user)
        pre_text_min3 = await lg_check2('minutes', 'минут', 'daqiqa', message.user)
        pre_text_sec1 = await lg_check2('second', 'секунда', 'soniya', message.user)
        pre_text_sec2 = await lg_check2('seconds', 'секунды', 'soniya', message.user)
        pre_text_sec3 = await lg_check2('seconds', 'секунд', 'soniya', message.user)

        start_time = data_all.get('start_time')
        time_now = time.time()
        elapsed_time = time_now - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)

        def time_formatter():
            if hours == 1:
                hours_text = f"1 {pre_text_hour1} "
            elif 2 <= hours < 5:
                hours_text = f"{hours} {pre_text_hour2} "
            else:
                hours_text = f"{hours} {pre_text_hour3} "
            if hours == 0:
                hours_text = ''

            if minutes == 1:
                minutes_text = f"1 {pre_text_min1}  "
            elif 2 <= hours < 5:
                minutes_text = f"{minutes} {pre_text_min2} "
            else:
                minutes_text = f"{minutes} {pre_text_min3} "
            if minutes == 0:
                minutes_text = ''

            if seconds == 1:
                seconds_text = f"1 {pre_text_sec1} "
            elif 2 <= hours < 5:
                seconds_text = f"{seconds} {pre_text_sec2} "
            else:
                seconds_text = f"{seconds} {pre_text_sec3} "
            if seconds == 0:
                seconds_text = ''
            return hours_text + minutes_text + seconds_text

        def correct_answers_org_var_func(key):
            if key == 'inc':
                if correct_answers_org:
                    correct_answers_org_var = ''
                    for num, (a, b) in enumerate(zip(correct_answers_org, correct_answers), 1):
                        correct_answers_org_var += f'`{num}. {a} -- {b}`\n'
                    correct_answers_org_var += '\n'
                    return correct_answers_org_var
            else:
                if correct_answers_mis:
                    correct_answers_org_var_mis = ''
                    for num, (a, b) in enumerate(zip(correct_answers_org_mis, correct_answers_mis), 1):
                        correct_answers_org_var_mis += f'`{num}. {a} -- {b}`\n'
                    return correct_answers_org_var_mis
            return ''

        def is_zero(key_zero):
            if key_zero == 'inc':
                if incorrect != 0:
                    return f'{pre_text6}\n'
            elif key_zero == 'mis':
                if missed != 0:
                    return pre_text5
            return ''

        def progress_is_good(progress_value):
            if progress > 0:
                return f'🔺 {progress_value}'
            elif progress == 0:
                return f'{progress_value}'
            else:
                return f'🔻 {progress_value}'

        def emoji_is_good(progress_emoji):
            if progress_emoji > 0:
                return '📈'
            else:
                return '📉'

        hashtag_text = ''
        for i in units:
            hashtag_text += f'#u{i} '

        async def rank_text_generator(rank):
            print(rank)
            if rank < 0:
                rank = abs(rank)
                rank_text = await lg_check2(f"🏁 Number of users you passed: <b>{rank}</b>",
                                            f"🏁 Количество пользователей, которых вы обошли: <b>{rank}</b>",
                                            f"🏁 Siz o'tib ketgan foydalanuvchilaringiz soni: <b>{rank}</b>",
                                            message.user)
                rank_text += '\n'
            else:
                rank_text = ''
            return rank_text

        pre_text = (f"📈 *{pre_text1}:*\n"  # Your results
                    f"#Book{book}\n"  # hashtags
                    f"🖇️ _Units:_ {hashtag_text}\n\n"  # hashtags

                    f"❓ _{pre_text2}:_ *{total}*\n"  # Total questions
                    f"💯 _{pre_text2_5}:_ *{per_round}%*\n"  # Percentage
                    f"{emoji_is_good(progress)} _{pre_text2_6}:_ *{progress_is_good(progress)}%*\n"  # Progress
                    f"☑️ _{pre_text3}:_ *{correct}*\n"  # Correct
                    f"❌ _{pre_text4}:_ *{incorrect}*\n"  # Incorrect
                    f"🔄 _{pre_text5}:_ *{missed}*\n"  # Missed
                    f"⌛️ *{time_formatter()}*\n"  # timer
                    '\n'
                    f"*{is_zero('inc')}*"  # Your incorrect answers
                    f"{correct_answers_org_var_func('inc')}"  # list ^

                    f"*{is_zero('mis')}*\n"  # Your missed answers
                    f"{correct_answers_org_var_func('mis')}\n"  # list ^\
                    f"🤖 {pre_text7}"
                    )

        if coins_different > 0:
            coin_text_en = (f"<b>You have earned {coins_different} 🪙</b>\n\n"
                            f"<i>💰 Your balance: {all_coins} 🪙</i>\n"
                            f"<i>{await rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Your place in Top 10: /top10</i>")

            coin_text_ru = (f"<b>Вы получили {coins_different} 🪙</b>\n\n"
                            f"<i>💰 Ваш баланс: {all_coins} 🪙</i>\n"
                            f"<i>{await rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Ваше место в Топ-10: /top10</i>")

            coin_text_uz = (f"<b>Siz {coins_different} 🪙 oldingiz</b>\n\n"
                            f"<i>💰 Balansingiz: {all_coins} 🪙</i>\n"
                            f"<i>{await rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Top 10 dagi joyingiz: /top10</i>")
        else:
            coin_text_en = (f"<b>You couldn't get 🪙, improve your progress!</b>\n\n"
                            f"<i>💰 Your balance: {all_coins} 🪙</i>\n"
                            f"<i>{await rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Your place in Top 10: /top10</i>")

            coin_text_ru = (f"<b>Вы не смогли получить 🪙, улучшайте прогресс!</b>\n\n"
                            f"<i>💰 Ваш баланс: {all_coins} 🪙</i>\n"
                            f"<i>{await rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Ваше место в Топ-10: /top10</i>")

            coin_text_uz = (f"<b>Siz 🪙 ololmadingiz, progresni oshiring!</b>\n\n"
                            f"<i>💰 Balansingiz: {all_coins} 🪙</i>\n"
                            f"<i>{await rank_text_generator(rank_dif)}</i>"
                            f"<i>📈 Top 10 dagi joyingiz: /top10</i>")
        coin_text = await lg_check2(coin_text_en, coin_text_ru, coin_text_uz, message.user)

        await bot.send_message(message.user.id, pre_text,
                               reply_markup=row1([await lg_check2("🏠 Main Menu", "🏠 Главное Меню",
                                                                  "🏠 Asosiy Menyu", message.user)]),
                               parse_mode="MARKDOWN")
        await bot.send_message(message.user.id, coin_text)
        pre_text_admin = f"#quiz\n{coin_text}\n{message.user.first_name} - {message.user.id} - @{message.user.username}"
        await bot.send_message(group, pre_text_admin)
        await bot.send_message(group, pre_text, parse_mode="MARKDOWN")
        await state.clear()

    @on.message(F.text.in_(["🚫 Stop", "🚫 Остановить", "🚫 To'xtatish"]))
    async def exit(self, message: Message) -> None:
        await self.wizard.exit()

    @on.poll_answer()
    async def answer(self, poll_answer: PollAnswer, state: FSMContext):
        data = await state.get_data()
        wrem = user_data.get(poll_answer.user.id)
        step = data["step"]
        answers = data.get("answers", {})
        option_ids = wrem.get('option_ids')
        ques_id = wrem.get('ques_id')
        index_of_random_answers = wrem.get('index_of_random_answers')
        option_index = index_of_random_answers[poll_answer.option_ids[0]]
        index_of_random_answers.clear()
        option = option_ids[ques_id[0]].get(option_index)
        answers[step] = option

        wrem['index_of_random_answers'] = index_of_random_answers
        await state.update_data(answers=answers)
        await self.wizard.retake(step=step + 1)
