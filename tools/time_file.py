from datetime import datetime

import pytz

TIMEZONE = 'Asia/Tashkent'


def timefunc(which):
    current_time = datetime.now(pytz.timezone(TIMEZONE))
    if which == 'today':
        return current_time.strftime('%d.%m.%y')
    elif which == 'time':
        return current_time.strftime('%H:%M')
