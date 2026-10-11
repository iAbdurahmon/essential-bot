import logging

from aiogram import F, Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, KICKED
from aiogram.types import ChatMemberUpdated

from tools.db_conn import execute

router = Router()
router.my_chat_member.filter(F.chat.type == "private")
router.message.filter(F.chat.type == "private")

logger = logging.getLogger(__name__)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def kicked(event: ChatMemberUpdated):
    execute('UPDATE users SET status = %s WHERE tg_id = %s', (0, event.from_user.id))
    logger.info('user %s blocked the bot', event.from_user.id)
