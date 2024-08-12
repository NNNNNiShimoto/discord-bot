# My Discord Bot
My DiscordBot inspired by LINE app. You can use amidakuji(ladder lottery), Rock-Paper-Scissors, and statistics function

## versions
```
python 3.11.4
discord.py 2.3.2
numpy 2.0.0
matplotlib 3.9.1
PIL 10.3.0
dotenv 1.0.1
```

## setup
- .env
    - Write your bot token, server id, font path, time zone
- data/names.py
    - write id, owner, dispname in id2owner, owner2id, id2dispname, is_join_list, admin_ids
        - id: each account discord id
        - owner: if you have two discord accounts, use same owner and you can share your configs, stats, etx
        - dispname: name displayed in the server
- data/config.json
    - write owner
- amida.py
    - font path
- stats.py
    - fontpath
    - timezone

## Statistics Data Structure
in data/stats/year_YYY/month_MM.json
- user
    - days
        - [0]*days
            - 3bit
            - --X ...whether user is logged by bot in the day
            - -X- ...whether user participate in VC in the day
            - X-- ...whether user started VC in the day
    - intime
        - [timestamp]*days
            - the time user joined in VC
    - outtime
        - [timestamp]*days
            - the time user quitted VC
    - lastjoin
        - the most recent VC participant time 　
    - timesec
        - the sum of VC time (second)
    - post
        - the number of user's post in one month. yet not included in system now.
    - botuse
        - the number of user's bot use in one month
    - react
        - the number of user's reaction in one month. yet not included in system now.