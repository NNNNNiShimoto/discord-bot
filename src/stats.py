import json
import datetime
import calendar
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from zoneinfo import ZoneInfo
from os.path import isfile, isdir
from os import makedirs
from data.names import owner2id

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
STATS_RANGE = 7
FONT_PATH = '/usr/your/favorite/font/path'
TIME_ZONE = "Country/City"

def createMonthJson(path, days):
    eachobj = {
        "days": [0]*days, 
        "intime": [None]*days,
        "outtime": [None]*days,
        "lastjoin": None,
        "timesec": 0,
        "post": 0,
        "botuse": 0,
        "react": 0,
        "imgnum": 0,
        "lettersum": 0
    }
    jobj = {owner : eachobj for owner in owner2id.keys()}
    with open(path,'w') as f:
        json.dump(jobj, f, indent=4)
    
def readMonthJson(path) -> dict[str, dict[str, any]]:
    with open(path,'r') as f:
        return json.load(f)

def getMonthJson(year: int, month: int):
    dirpath = f"data/stats/year_{year}"
    if not isdir(dirpath):
        makedirs(dirpath)
    path = f"data/stats/year_{year}/month_{str(month).zfill(2)}.json"
    _, days = calendar.monthrange(year, month)
    if not isfile(path):
        createMonthJson(path, days)
    return readMonthJson(path)

def saveMonthJson(jobj, year: int, month: int):
    path = f"data/stats/year_{str(year)}/month_{str(month).zfill(2)}.json"
    if isfile(path):
        with open(path,'w') as f:
            json.dump(jobj, f, indent=4)
    else: 
        print('saveMonthJson(): File not found')

def joinLog(owner: str, is_first: bool):
    dt_now = datetime.datetime.now(ZoneInfo(TIME_ZONE))
    jobj = getMonthJson(dt_now.year, dt_now.month)

    if jobj[owner]["intime"][dt_now.day-1] is None:
        jobj[owner]["intime"][dt_now.day-1] = [dt_now.hour*60*60+dt_now.minute*60+dt_now.second]
    else:
       jobj[owner]["intime"][dt_now.day-1].append(dt_now.hour*60*60+dt_now.minute*60+dt_now.second)

    jobj[owner]["lastjoin"] = dt_now.strftime(TIME_FORMAT)

    if jobj[owner]["days"][dt_now.day-1]%4//2 == 0:
        jobj[owner]["days"][dt_now.day-1] += 6 if is_first else 2
    
    saveMonthJson(jobj, dt_now.year, dt_now.month)

def quitLog(owner: str):
    dt_now = datetime.datetime.now(ZoneInfo(TIME_ZONE))
    jobj = getMonthJson(dt_now.year, dt_now.month)

    if jobj[owner]["outtime"][dt_now.day-1] is None:
        jobj[owner]["outtime"][dt_now.day-1] = [dt_now.hour*60*60+dt_now.minute*60+dt_now.second]
    else:
        jobj[owner]["outtime"][dt_now.day-1].append(dt_now.hour*60*60+dt_now.minute*60+dt_now.second)
    
    if jobj[owner]["lastjoin"] is not None:
        delta = dt_now - datetime.datetime.strptime(jobj[owner]["lastjoin"], TIME_FORMAT).replace(tzinfo=ZoneInfo('Asia/Tokyo'))
        jobj[owner]["timesec"] +=  delta.days*86400 + delta.seconds
        jobj[owner]["lastjoin"] = None
    else: #month changed 
        dt_before = dt_now - datetime.timedelta(days=1)
        jobj_b = getMonthJson(dt_before.year, dt_before.month)
        if jobj_b[owner]["lastjoin"] is None: # more than one month joined or error
            print("err")
        else:
            b_delta = (
                datetime.datetime(year=dt_before.year, month=dt_before.month, day=dt_before.day, hour=23, minute=59, second=59) 
              - datetime.datetime.strptime(jobj_b[owner]["lastjoin"], TIME_FORMAT).replace(tzinfo=ZoneInfo('Asia/Tokyo')))
            jobj_b[owner]["timesec"] +=  b_delta.days*86400 + b_delta.seconds
            jobj_b[owner]["lastjoin"] = None
            saveMonthJson(jobj_b, dt_before.year, dt_before.month)

            delta = (dt_now - datetime.datetime(year=dt_now.year, month=dt_now.month, day=dt_now.day))
            jobj[owner]["timesec"] +=  delta.days*86400 + delta.seconds
            

    saveMonthJson(jobj, dt_now.year, dt_now.month)

def countLog(type: str, owner: str, plus: int):
    dt_now = datetime.datetime.now(ZoneInfo(TIME_ZONE))
    jobj = getMonthJson(dt_now.year, dt_now.month)

    jobj[owner][type]+= plus
    if jobj[owner]["days"][dt_now.day-1]%2 == 0:
        jobj[owner]["days"][dt_now.day-1]+=1
    
    saveMonthJson(jobj, dt_now.year, dt_now.month)

#TODO: include in main.py
def postLog(owner: str):
    countLog("post", owner, 1)

def botuseLog(owner: str):
    countLog("botuse", owner, 1)

#TODO: include in main.py
def reactLog(owner: str):
    countLog("react", owner, 1)

#create one week VC join graph for one person
def getOneweekStats(owner: str):
    dt_now = datetime.datetime.now(ZoneInfo(TIME_ZONE))
    if dt_now.day < STATS_RANGE:
        dt_before = dt_now - datetime.timedelta(days=STATS_RANGE)
        jobj_b = getMonthJson(dt_before.year, dt_before.month)
        jobj = getMonthJson(dt_now.year, dt_now.month)
        ticklist = [f"{dt_before.month}/{i+dt_before.day}\n0:00" for i in range(STATS_RANGE-dt_now.day)]+[f"{dt_now.month}/{i+1}\n0:00" for i in range(dt_now.day+1)]

        join_list = jobj_b[owner]["intime"][-STATS_RANGE+dt_now.day:] + jobj[owner]["intime"][:dt_now.day]
        quit_list = jobj_b[owner]["outtime"][-STATS_RANGE+dt_now.day:] + jobj[owner]["outtime"][:dt_now.day]

    else:
        jobj = getMonthJson(dt_now.year, dt_now.month)
        dt_after = dt_now + datetime.timedelta(days=1)
        ticklist = [f"{dt_now.month}/{dt_now.day-6+i}\n0:00" for i in range(7)]
        ticklist.append(f"{dt_after.month}/{dt_after.day}\n0:00")
        join_list = jobj[owner]["intime"][dt_now.day-7:dt_now.day]
        quit_list = jobj[owner]["outtime"][dt_now.day-7:dt_now.day]

    if jobj[owner]["lastjoin"] is not None:
        if quit_list[-1] is None:
            quit_list[-1] = [dt_now.hour*60*60+dt_now.minute*60+dt_now.second]
        else:
            quit_list[-1].append(dt_now.hour*60*60+dt_now.minute*60+dt_now.second)
    
    join_p = [i*86400+j for i in range(STATS_RANGE) if join_list[i] is not None for j in join_list[i]]
    quit_p = [i*86400+j for i in range(STATS_RANGE) if quit_list[i] is not None for j in quit_list[i]]

    if len(join_p) == len(quit_p)-1:
        join_p.insert(0,0)
    if len(join_p) != len(quit_p):
        print("error! json data is broken")
        return None
    
    x, y =[0], [0]
    for i in range(len(join_p)):
        x.extend([join_p[i], join_p[i], quit_p[i], quit_p[i]])
        y.extend([0, 1, 1, 0])
    x.append(STATS_RANGE*24*60)
    y.append(0)
    
    #for graph design
    fm.fontManager.addfont(FONT_PATH)
    prop = fm.FontProperties(fname=FONT_PATH)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = prop.get_name()

    fig, ax = plt.subplots(figsize=(8,2))
    fig.set_facecolor('#36393f')
    ax.set_facecolor('#36393f')
    ax.tick_params(axis='both', colors='#dcddde')

    for spine in ax.spines.values():
        spine.set_edgecolor('#dcddde')
        
    ax.grid(axis="both", which="major", color='#666666')

    plt.fill_between(x, y, color='#5865F2', alpha=0.6)
    plt.plot(x, y, color='#5865F2', alpha=1)
    plt.xlim(0,STATS_RANGE*86400)
    plt.xticks(range(0,STATS_RANGE*86400+1000,86400), ticklist, fontweight='bold')
    plt.ylim(0,1.5)
    plt.yticks([])
    path = f"img/dynamic/graph_{owner}.png"
    plt.savefig(path, dpi=200, bbox_inches = 'tight', pad_inches = 0.05)
    plt.close()
    return path

#create one night VC join graph for all members
def getOneNightStats(year: int, month: int, day: int):
    now = datetime.datetime.now()
    try:
        target = datetime.datetime(year=year, month=month, day=day)
    except ValueError:
        print('getOneNightStats(): Invalid Date')
        return None
    
    if now <= target:
        print('getOneNightStats(): Future Date is invalid')
        return None
    
    target_before = target - datetime.timedelta(days=1)

    if target_before.month == target.month:
        jobj = getMonthJson(target.year, target.month)
        join_1 = [jobj[owner]["intime"][target.day-2] for owner in jobj]
        quit_1 = [jobj[owner]["outtime"][target.day-2] for owner in jobj]
        join_2 = [jobj[owner]["intime"][target.day-1] for owner in jobj]
        quit_2 = [jobj[owner]["outtime"][target.day-1] for owner in jobj]

    else:
        jobj_b = getMonthJson(target_before.year, target_before.month)
        jobj_t = getMonthJson(target.year, target.month)
        join_1 = [jobj_b[owner]["intime"][target.day-2] for owner in jobj_b]
        quit_1 = [jobj_b[owner]["outtime"][target.day-2] for owner in jobj_b]
        join_2 = [jobj_t[owner]["intime"][target.day-1] for owner in jobj_t]
        quit_2 = [jobj_t[owner]["outtime"][target.day-1] for owner in jobj_t]

    target_next = target + datetime.timedelta(days=1)
    ticks = ([str(target_before.month)+"/"+str(target_before.day)+"\n0:00", "\n12:00"]
             +[str(target.month)+"/"+str(target.day)+"\n0:00", "\n12:00"]
             +[str(target_next.month)+"/"+str(target_next.day)+"\n0:00"])
    
    if target_next > now:
        for idx, owner in enumerate(jobj):
            if jobj[owner]["lastjoin"] is not None:
                if quit_2[idx] is None:
                    quit_2[idx] = [now.hour*60*60+now.minute*60+now.second]
                else:
                    quit_2[idx].append(now.hour*60*60+now.minute*60+now.second)

    first_num = 0
    for i in range(len(join_1)):
        if quit_1[i] is not None:
            if join_1[i] is not None and (join_1[i][0] < quit_1[i][0]):
                pass 
            else: first_num += 1
        elif join_1[i] is None:
            if quit_2[i] is not None and (join_2[i] is None or (join_2[i] is not None and (join_2[i][0] > quit_2[i][0]))):
                first_num += 1

    timestamp = (  [(elem,       True) for l in join_1 if l is not None for elem in l] 
                 + [(elem+86400, True) for l in join_2 if l is not None for elem in l]
                 + [(elem,      False) for l in quit_1 if l is not None for elem in l]
                 + [(elem+86400,False) for l in quit_2 if l is not None for elem in l])
    timestamp.sort()

    person_num = first_num
    x, y =[0], [person_num]
    for i in range(len(timestamp)):
        x.extend([timestamp[i][0],timestamp[i][0]])
        if timestamp[i][1]:
            y.extend([person_num, person_num+1])
            person_num += 1
        else:
            y.extend([person_num, person_num-1])
            person_num -= 1
    x.append(2*86400)
    y.append(person_num)

    # for graph design
    fm.fontManager.addfont(FONT_PATH)
    prop = fm.FontProperties(fname=FONT_PATH)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = prop.get_name()

    fig, ax = plt.subplots(figsize=(5,2))
    fig.set_facecolor('#36393f')
    ax.set_facecolor('#36393f')
    ax.tick_params(axis='both', colors='#dcddde')

    for spine in ax.spines.values():
        spine.set_edgecolor('#dcddde')
        
    ax.grid(axis="both", which="major", color='#666666')

    plt.fill_between(x, y, color='#5865F2', alpha=0.6)
    plt.plot(x, y, color='#5865F2', alpha=1)
    plt.xlim(0,2*86400)
    plt.xticks(range(0,2*86400+1000,86400//2), ticks)
    plt.ylim(0,len(owner2id.keys())+1)
    plt.yticks(range(0,8), list(range(0,8)))
    path = "img/dynamic/graph_all.png"
    plt.savefig(path, dpi=200, bbox_inches = 'tight', pad_inches = 0.05)
    plt.close()
    return path

#function for create calendar
def getDaysStats(owner: str, year: int, month: int, is_used_discord: bool=True):
    jobj = getMonthJson(year, month)
    if is_used_discord:
        return [elem > 1 for elem in jobj[owner]["days"]]
    else:
        return [elem//2 for elem in jobj[owner]["days"]]
