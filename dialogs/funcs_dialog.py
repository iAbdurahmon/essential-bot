import logging

from aiogram import Bot

from tools.db_conn import fetch_all
from lg_messages.func import lg_check4_lg_id, lg_checker2

logger = logging.getLogger(__name__)

TOP_SIZE = 10

RATING_QUERY = ('SELECT tg_id FROM users WHERE status = 1 '
                'ORDER BY CASE WHEN rank IS NULL THEN 1 ELSE 0 END, rank DESC')


def top_all_checker():
    return {place: row[0] for place, row in enumerate(fetch_all(RATING_QUERY), 1)}


def top_checker(user_id):
    for place, tg_id in top_all_checker().items():
        if tg_id == int(user_id):
            return place


async def notify_overtaken(bot: Bot, user_id: int, before: dict, after: dict):
    # before/after are {place: tg_id} snapshots of the rating taken around a coin update
    places_before = {tg_id: place for place, tg_id in before.items()}
    places_after = {tg_id: place for place, tg_id in after.items()}

    place_before = places_before.get(user_id)
    place_after = places_after.get(user_id)
    if place_before is None or place_after is None or place_after >= place_before:
        return

    # everyone the user jumped over moved exactly one place down
    for place in range(place_after, place_before):
        passed_id = after.get(place + 1)
        if passed_id is None or places_before.get(passed_id, 0) > TOP_SIZE:
            continue
        lost_text = lg_check4_lg_id(
            f"🏁 <b>You've been overtaken!</b>\nNow you are <b>{place + 1}</b> in Top {TOP_SIZE}",
            f"🏁 <b>Вас обогнали!</b>\nТеперь вы {place + 1} в Топ-{TOP_SIZE}",
            f"🏁 <b>Sizdan o'zib ketishdi!</b>\nEndi siz Top {TOP_SIZE} taligida <b>{place + 1}</b>siz",
            lg_checker2(passed_id))
        try:
            await bot.send_message(passed_id, lost_text)
        except Exception as e:
            logger.warning('could not notify %s about losing a place: %s', passed_id, e)
