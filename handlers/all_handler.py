from aiogram import F, Router, Bot
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated

from tools.db_conn import cur, conn
from data_small import group

router = Router()
router.my_chat_member.filter(F.chat.type == "private")
router.message.filter(F.chat.type == "private")


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def kicked(event: ChatMemberUpdated, bot: Bot):
    cur.execute('UPDATE users SET status = %s WHERE tg_id = %s', (0, f"{event.from_user.id}"))
    conn.commit()
    await bot.send_message(group, f"<b>DELETED:</b>\n{event.from_user.first_name}\n"
                                      f"@{event.from_user.username}\n"
                                      f"{event.from_user.id}", parse_mode='html')
    print(f"{event.from_user.id} - deleted")
