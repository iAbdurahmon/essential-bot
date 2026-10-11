from datetime import datetime
from threading import Timer
import pytz

# time = None
# def timefunc():
#     current_time = datetime.now()
#     tz_tashkent = pytz.timezone('Asia/Tashkent')
#     current_time_tashkent = current_time.astimezone(tz_tashkent)
#     today = current_time_tashkent.strftime('%d.%m.%y')
#     time = current_time_tashkent.strftime('%H:%M')
#     t = Timer(1, timefunc)
#     t.start()
#     return time
# timefunc()


def timefunc(which):
    current_time = datetime.now()
    tz_tashkent = pytz.timezone('Asia/Tashkent')
    current_time_tashkent = current_time.astimezone(tz_tashkent)
    today = current_time_tashkent.strftime('%d.%m.%y')
    time = current_time_tashkent.strftime('%H:%M')
    if which == 'today':
        return today
    elif which == 'time':
        return time

