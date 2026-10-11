import logging
import random
import time

from typing import Any
from collections import Counter

from aiogram import Bot
from aiogram import Router, F
from aiogram.fsm.scene import Scene, on
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PollAnswer, User
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tools.db_conn import cur, conn
from tools.mongo_queries import update_coins, select_coin
from data_small import *
from lg_messages.func import lg_check4_lg_id, lg_checker2
from keyboards.reply import row1
from dialogs.funcs_dialog import top_all_checker, notify_overtaken

router_poll = Router()
logger = logging.getLogger(__name__)

OPTIONS_COUNT = 4
POLL_PERIOD = 30
COINS_PER_ANSWER = 2

STOP_BUTTONS = ["🚫 Stop", "🚫 Остановить", "🚫 To'xtatish"]
NEXT_BUTTONS = ["➡️ Next", "➡️ Пропустить", "➡️ Kengisi"]

TIME_WORDS = {
    'hour': (('hour', 'hours', 'hours'), ('час', 'часа', 'часов'), ('soat', 'soat', 'soat')),
    'minute': (('minute', 'minutes', 'minutes'), ('минута', 'минуты', 'минут'),
               ('daqiqa', 'daqiqa', 'daqiqa')),
    'second': (('second', 'seconds', 'seconds'), ('секунда', 'секунды', 'секунд'),
               ('soniya', 'soniya', 'soniya')),
}


def build_questions(book, units, from_lg, to_lg):
    questions = []
    for unit in units:
        cur.execute(f"SELECT {from_lg}, {to_lg} FROM book{book} WHERE unit = %s", (unit,))
        rows = cur.fetchall()
        # wrong options come from the same unit, duplicates would make two identical buttons
        pool = list(dict.fromkeys(answer.strip() for _, answer in rows if answer))
        for word, correct in rows:
            if not word or not correct:
                continue
            distractors = [w for w in pool if w != correct.strip()]
            if len(distractors) < OPTIONS_COUNT - 1:
                logger.warning('book%s unit%s has too few words for a question', book, unit)
                continue
            options = random.sample(distractors, OPTIONS_COUNT - 1) + [correct]
            # shuffled once, here: the stored order is the order Telegram will show
            random.shuffle(options)
            questions.append({'text': word, 'options': options,
                              'correct': correct, 'unit': unit})
    random.shuffle(questions)
    return questions


def quiz_keyboard(lg):
    markup = ReplyKeyboardBuilder()
    markup.button(text=f"""🚫 {lg_check4_lg_id('Stop', 'Остановить', "To'xtatish", lg)}""")
    markup.button(text=f"➡️ {lg_check4_lg_id('Next', 'Пропустить', 'Kengisi', lg)}")
    return markup.adjust(2).as_markup(resize_keyboard=True)


def plural(value, kind, lg):
    if not value:
        return ''
    forms = lg_check4_lg_id(*TIME_WORDS[kind], lg)
    if value == 1:
        word = forms[0]
    elif 2 <= value < 5:
        word = forms[1]
    else:
        word = forms[2]
    return f"{value} {word} "


def elapsed_text(seconds_total, lg):
    hours = int(seconds_total // 3600)
    minutes = int((seconds_total % 3600) // 60)
    seconds = int(seconds_total % 60)
    return (plural(hours, 'hour', lg)
            + plural(minutes, 'minute', lg)
            + plural(seconds, 'second', lg)).strip()


def share(coins, total):
    if not total:
        return 0
    return coins * 100 / (total * COINS_PER_ANSWER)


def pairs_text(pairs):
    return ''.join(f'`{num}. {word} -- {answer}`\n' for num, (word, answer) in enumerate(pairs, 1))


class QuizScene(Scene, state="quiz"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, step: int | None = 0) -> Any:
        if not step and not await self.prepare(message.from_user, state):
            lg = lg_checker2(message.from_user.id)
            await message.answer(lg_check4_lg_id(
                "❌ There are no words for the selected units yet.",
                "❌ Для выбранных unit пока нет слов.",
                "❌ Tanlangan unitlar uchun hozircha so'zlar yo'q.", lg))
            return await self.wizard.exit()
        return await self.ask(message.bot, message.from_user.id, state, step or 0)

    @on.poll_answer.enter()
    async def on_poll_enter(self, poll_answer: PollAnswer, bot: Bot, state: FSMContext,
                            step: int | None = 0) -> Any:
        return await self.ask(bot, poll_answer.user.id, state, step or 0)

    async def prepare(self, user: User, state: FSMContext) -> bool:
        settings = user_data.get(user.id)
        if not settings:
            logger.warning('quiz started without settings for %s', user.id)
            return False
        questions = build_questions(settings['book'], settings['units'],
                                    lg_reductions[settings['from']],
                                    lg_reductions[settings['to']])
        if not questions:
            return False
        await state.update_data(questions=questions, answers={}, start_time=time.time(),
                                lg=lg_checker2(user.id),
                                book=settings['book'], units=settings['units'])
        return True

    async def ask(self, bot: Bot, chat_id: int, state: FSMContext, step: int) -> Any:
        data = await state.get_data()
        questions = data.get('questions') or []
        if step >= len(questions):
            return await self.wizard.exit()

        quiz = questions[step]
        await state.update_data(step=step)
        return await bot.send_poll(
            chat_id=chat_id,
            question=f"{step + 1}. {quiz['text']}",
            options=quiz['options'],
            correct_option_id=quiz['options'].index(quiz['correct']),
            is_anonymous=False,
            type='quiz',
            open_period=POLL_PERIOD,
            reply_markup=quiz_keyboard(data['lg'])
        )

    @on.poll_answer()
    async def answer(self, poll_answer: PollAnswer, state: FSMContext):
        data = await state.get_data()
        step = data.get('step', 0)
        questions = data.get('questions') or []
        if step >= len(questions):
            return

        # options were stored in the order Telegram showed them, so the id maps straight back
        options = questions[step]['options']
        chosen = poll_answer.option_ids[0]
        answers = data.get('answers', {})
        if chosen < len(options):
            answers[str(step)] = options[chosen]
        await state.update_data(answers=answers)
        await self.wizard.retake(step=step + 1)

    @on.message(F.text.in_(NEXT_BUTTONS))
    async def skip(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        await self.wizard.retake(step=data.get('step', 0) + 1)

    @on.message(F.text.in_(STOP_BUTTONS))
    async def stop(self, message: Message) -> None:
        await self.wizard.exit()

    @on.message.exit()
    async def on_exit(self, message: Message, bot: Bot, state: FSMContext) -> None:
        await self.finish(bot, message.from_user, state)

    @on.poll_answer.exit()
    async def on_poll_exit(self, poll_answer: PollAnswer, bot: Bot, state: FSMContext) -> None:
        await self.finish(bot, poll_answer.user, state)

    async def finish(self, bot: Bot, user: User, state: FSMContext) -> None:
        data = await state.get_data()
        questions = data.get('questions')
        user_data.pop(user.id, None)
        if not questions:
            await state.clear()
            return

        lg = data.get('lg') or lg_checker2(user.id)
        answers = data.get('answers', {})
        last_step = data.get('step', 0)
        book = data['book']
        units = data['units']

        correct = 0
        incorrect = 0
        missed = 0
        wrong_pairs = []
        missed_pairs = []
        correct_units = []
        for step, quiz in enumerate(questions):
            answer = answers.get(str(step))
            if answer == quiz['correct']:
                correct += 1
                # the unit is known from the question itself, no lookup by answer text
                correct_units.append(quiz['unit'])
            elif answer is None:
                missed += 1
                missed_pairs.append((quiz['text'], quiz['correct']))
            else:
                incorrect += 1
                wrong_pairs.append((quiz['text'], quiz['correct']))
            if step == last_step:
                break

        # total counts every word in the selected units, that is what progress is measured against
        total = len(questions)
        per_round = round(correct * 100 / total, 1) if total else 0

        unit_counts = Counter(correct_units)
        old_coins = 0
        for unit in unit_counts:
            earned = select_coin(user.id, book, unit)
            if earned is None:
                logger.warning('no balance in mongo for %s, book%s unit%s', user.id, book, unit)
                earned = 0
            old_coins += earned

        new_coins = correct * COINS_PER_ANSWER
        progress = round(share(new_coins, total) - share(old_coins, total), 1)
        if progress > 0:
            for unit, hits in unit_counts.items():
                update_coins(user.id, book, unit, hits * COINS_PER_ANSWER)
        else:
            new_coins = old_coins

        cur.execute('SELECT rank FROM users WHERE tg_id = %s', (str(user.id),))
        row = cur.fetchone()
        coins_different = new_coins - old_coins
        all_coins = ((row[0] or 0) if row else 0) + coins_different

        before = top_all_checker()
        cur.execute('UPDATE users SET rank = %s WHERE tg_id = %s', (all_coins, str(user.id)))
        conn.commit()
        after = top_all_checker()
        await notify_overtaken(bot, user.id, before, after)

        places_before = {tg_id: place for place, tg_id in before.items()}
        places_after = {tg_id: place for place, tg_id in after.items()}
        passed = places_before.get(user.id, 0) - places_after.get(user.id, 0)

        await bot.send_message(user.id, self.result_text(data, lg, book, units, total, per_round,
                                                         progress, correct, incorrect, missed,
                                                         wrong_pairs, missed_pairs),
                               reply_markup=row1([lg_check4_lg_id("🏠 Main Menu", "🏠 Главное Меню",
                                                                  "🏠 Asosiy Menyu", lg)]),
                               parse_mode="MARKDOWN")
        await bot.send_message(user.id, self.coins_text(lg, coins_different, all_coins, passed))
        await state.clear()

    def result_text(self, data, lg, book, units, total, per_round, progress,
                    correct, incorrect, missed, wrong_pairs, missed_pairs):
        title = lg_check4_lg_id('Your results', 'Ваши результаты', 'Sizning natijalaringiz', lg)
        questions_label = lg_check4_lg_id('Total questions', 'Всего вопросов', 'Jami savollar', lg)
        percent_label = lg_check4_lg_id('Percentage', 'Процент', 'Foiz', lg)
        progress_label = lg_check4_lg_id('Progress', 'Прогресс', 'Progres', lg)
        correct_label = lg_check4_lg_id('Correct', 'Правильные', "Tog'ri", lg)
        incorrect_label = lg_check4_lg_id('Incorrect', 'Неправильные', "Noto'g'ri", lg)
        missed_label = lg_check4_lg_id('Missed', 'Пропущенные', "O'tkazib yuborilgan", lg)
        wrong_title = lg_check4_lg_id('Your incorrect answers:', 'Ваши неправильные ответы:',
                                      "Sizning noto'g'ri javoblaringiz:", lg)
        footer = lg_check4_lg_id(
            "Use a bot to learn new words: @essentialwordstestbot",
            "Используйте бота для изучения новых слов: @essentialwordstestbot",
            "Yangi so'zlarni o'rganish uchun botdan foydalaning: @essentialwordstestbot", lg)

        elapsed = elapsed_text(time.time() - data.get('start_time', time.time()), lg)
        hashtags = ' '.join(f'#u{unit}' for unit in units)
        trend = '📈' if progress > 0 else '📉'
        arrow = '🔺 ' if progress > 0 else ('🔻 ' if progress < 0 else '')

        wrong_block = f"*{wrong_title}*\n{pairs_text(wrong_pairs)}\n" if wrong_pairs else ''
        missed_block = f"*{missed_label}*\n{pairs_text(missed_pairs)}\n" if missed_pairs else ''

        return (f"📈 *{title}:*\n"
                f"#Book{book}\n"
                f"🖇️ _Units:_ {hashtags}\n\n"
                f"❓ _{questions_label}:_ *{total}*\n"
                f"💯 _{percent_label}:_ *{per_round}%*\n"
                f"{trend} _{progress_label}:_ *{arrow}{progress}%*\n"
                f"☑️ _{correct_label}:_ *{correct}*\n"
                f"❌ _{incorrect_label}:_ *{incorrect}*\n"
                f"🔄 _{missed_label}:_ *{missed}*\n"
                f"⌛️ *{elapsed}*\n\n"
                f"{wrong_block}"
                f"{missed_block}"
                f"🤖 {footer}")

    def coins_text(self, lg, coins_different, all_coins, passed):
        passed_text = ''
        if passed > 0:
            passed_text = lg_check4_lg_id(
                f"🏁 Number of users you passed: {passed}\n",
                f"🏁 Количество пользователей, которых вы обошли: {passed}\n",
                f"🏁 Siz o'tib ketgan foydalanuvchilaringiz soni: {passed}\n", lg)

        if coins_different > 0:
            head = lg_check4_lg_id(f"<b>You have earned {coins_different} 🪙</b>",
                                   f"<b>Вы получили {coins_different} 🪙</b>",
                                   f"<b>Siz {coins_different} 🪙 oldingiz</b>", lg)
        else:
            head = lg_check4_lg_id("<b>You couldn't get 🪙, improve your progress!</b>",
                                   "<b>Вы не смогли получить 🪙, улучшайте прогресс!</b>",
                                   "<b>Siz 🪙 ololmadingiz, progresni oshiring!</b>", lg)

        balance = lg_check4_lg_id(f"💰 Your balance: {all_coins} 🪙",
                                  f"💰 Ваш баланс: {all_coins} 🪙",
                                  f"💰 Balansingiz: {all_coins} 🪙", lg)
        top = lg_check4_lg_id("📈 Your place in Top 10: /top10",
                              "📈 Ваше место в Топ-10: /top10",
                              "📈 Top 10 dagi joyingiz: /top10", lg)
        return f"{head}\n\n<i>{balance}\n{passed_text}{top}</i>"
