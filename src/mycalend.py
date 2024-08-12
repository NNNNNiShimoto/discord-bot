from PIL import Image
from src.stats import getDaysStats
from calendar import monthrange, isleap
from random import randrange

SPACE = 313
CORNER_X = 185
CORNER_Y = 2060

#create owner's monthly login calendar
#if is_used_discord is true, stamped on the day when owner's action is logged by bot
#else, stamped on the day when owner joins VC
def getCalendar(owner: str, year: int, month: int, is_used_discord: bool):
    monthly_login_list = getDaysStats(owner, year, month, is_used_discord)
    day_of_week, end_of_month = monthrange(year, month)
    if month == 2:
        if isleap(year):
            path = f'img/calendar/month_{str(month).zfill(2)}/leap/calend_{month}_{day_of_week}.png'
        else:
            path = f'img/calendar/month_{str(month).zfill(2)}/not_leap/calend_{month}_{day_of_week}.png'
    else:
        path = f'img/calendar/month_{str(month).zfill(2)}/calend_{month}_{day_of_week}.png'
    try:
        calend = Image.open(path).convert('RGBA')
        stamp = Image.open('img/stamp/hanko.png').convert('RGBA')
    except FileNotFoundError:
        print('getCalendar(): No such file')
        return None

    img_clear = Image.new("RGBA", calend.size, (255, 255, 255, 0))

    calend_height = (end_of_month-1+(day_of_week+1)%7)//7

    if is_used_discord:
        for i in range(end_of_month):
            if monthly_login_list[i]:
                img_clear.paste(
                    stamp.rotate(randrange(-20,21), expand=True), 
                    (CORNER_X+(day_of_week+1+i)%7*SPACE + randrange(-20,21), 
                    CORNER_Y-(calend_height-(i+(day_of_week+1)%7)//7)*SPACE + randrange(-20,21)))
    else:
        g_stamp = Image.open('img/stamp/open_hanko.png').convert('RGBA')
        for i in range(end_of_month):
            if monthly_login_list[i]//2>0:
                img_clear.paste(
                    g_stamp, 
                    (CORNER_X+(day_of_week+1+i)%7*SPACE, 
                    CORNER_Y-(calend_height-(i+(day_of_week+1)%7)//7)*SPACE))
            elif monthly_login_list[i]>0:
                img_clear.paste(
                    stamp, 
                    (CORNER_X+(day_of_week+1+i)%7*SPACE, 
                    CORNER_Y-(calend_height-(i+(day_of_week+1)%7)//7)*SPACE))
        g_stamp.close()
    
    calend = Image.alpha_composite(calend, img_clear)
    return_path = 'img/dynamic/calendar.png'
    calend.save(return_path)

    return return_path
