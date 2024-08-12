import random
import re

DICE_LIST = [
    ":one:",
    ":two:",
    ":three:",
    ":four:",
    ":five:",
    ":six:",
    ":seven:",
    ":eight:",
    ":nine:",
    ":zero:"
]

def parsexdy(xdy):
    dlist = re.split('[dD]', xdy)
    if len(dlist) != 2:
        return 1, 6
    if dlist[0].isdecimal() and dlist[1].isdecimal():
        return int(dlist[0]), int(dlist[1])
    else:
        return 1, 6

def dice(xdy: str):
    x, y = parsexdy(xdy)
    if x<1 or x>100 or y<1 or y>100:
        return None
    str=""
    if y<=10:
        for _ in range(x):
            str+= DICE_LIST[random.randrange(y)]+" "
    else:
        for _ in range(x):
            r = random.randrange(y)
            str+= DICE_LIST[r//10]+DICE_LIST[r%10]+" "
    return str
