import discord
from discord import app_commands
from discord.app_commands import describe
import os
import datetime
import random

import src.stats as stats
import src.amida as amida
import src.dice as dice
from rpsGame import createRPSGameView
from multiRPSGame import createMultiRPSGameView
from src.pages import createPagesView
from src.config import createConfigView
from src.mycalend import getCalendar
from data.names import id2owner, is_join_list, id2dispname, admin_ids, vcnum
from src.config import getNoticeIDList, resetIsNoticed

from dotenv import load_dotenv
load_dotenv()

client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)

GUILD_ID = int(os.getenv('GUILD_ID'))
    
def isJoin(guild: discord.Guild, owner: str):
    '''returns whether the same person is on VC with a different account.'''
    id_list = [list(id2owner.keys())[idx] for idx, value in enumerate(id2owner.values()) if value == owner]
    for id in id_list:
        if guild.get_member(id) is not None:
            if guild.get_member(id).voice is not None:
                return True
    return False

@client.event
async def on_ready():
    await tree.sync()
    print('-----Startup Success-----')

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if GUILD_ID != member.guild.id:
        return None
    global vcnum
    if before.channel is None: # JOINED
        if not is_join_list[id2owner[member.id]]:
            is_join_list[id2owner[member.id]] = True
            stats.joinLog(id2owner[member.id], vcnum == 0)
        vcnum += 1
        notice_ids = getNoticeIDList(vcnum=vcnum)
        for id in notice_ids:
            await member.guild.get_member(id).send('The call has started!')
    if after.channel is None: # QUITTED
        if not isJoin(member.guild, id2owner[member.id]):
            is_join_list[id2owner[member.id]] = False
            stats.quitLog(id2owner[member.id])
        vcnum -= 1
        if vcnum <= 0:
            resetIsNoticed()

@tree.command(name="amida", description="create a ladder lottery")
async def sendAmida(interaction: discord.Interaction, hit: int=1, items: str=""):
    stats.botuseLog(id2owner[interaction.user.id])
    amida_list = items.split()
    if len(amida_list)<2:
        e = amida.createAmida(random.sample(list(id2dispname.values()), len(id2dispname)), hit, 0)
    else :
        e = amida.createAmida(amida_list, hit, 0)
    if e: await interaction.response.send_message(content="Image generation failed.", ephemeral=True)
    else: await interaction.response.send_message(content=None, file=discord.File("img/dynamic/amida.jpg"))

@tree.command(name="help", description="display all commands descriptions")
async def help(interaction: discord.Interaction):
    stats.botuseLog(id2owner[interaction.user.id])
    await interaction.response.send_message(content="Loading...", ephemeral=True)
    await createPagesView(editor=await interaction.original_response(), pages="data/help.json")

@tree.command(name="d", description="roll the dice")
async def d(interaction: discord.Interaction, xdy: str="1d6"):
    stats.botuseLog(id2owner[interaction.user.id])
    s = dice.dice(xdy)
    if s is not None:
        await interaction.response.send_message(s)
    else:
        await interaction.response.send_message(content="Given number is too large", ephemeral=True)

@tree.command(name="rps", description="Play the Rock-Paper-Scissors-Game. First to max 10")
async def rps(interaction: discord.Interaction, bon: int=1):
    stats.botuseLog(id2owner[interaction.user.id])
    if abs(bon) > 10 or bon == 0:
        await interaction.response.send_message(content="Given number is too large", ephemeral=True)
    else:
        await interaction.response.send_message(content="Loading...", ephemeral=bon!=abs(bon))
        await createRPSGameView(editor=await interaction.original_response(), boN=bon)

@tree.command(name="mrps", description="Play the Rock-Paper-Scissors-Game with friends. First to max 10")
async def mulrps(interaction: discord.Interaction, bon: int=1, pl: int=2):
    stats.botuseLog(id2owner[interaction.user.id])
    if bon>10 or pl>len(id2owner):
        await interaction.response.send_message(content="Given number is too large.", ephemeral=True)
    elif bon < 1 or pl < 2:
        await interaction.response.send_message(content="Invalid arguments.", ephemeral=True)
    else:
        await interaction.response.send_message(content="Loading...")
        await createMultiRPSGameView(editor=await interaction.original_response(), id=interaction.user.id, boN=bon, player_num=pl)

@tree.command(name="stats", description="create a graph showing how many VC one user has participated in last one week")
async def sendStats(interaction: discord.Interaction, member: discord.Member):
    stats.botuseLog(id2owner[interaction.user.id])
    if member.id in id2owner.keys():
        path = stats.getOneweekStats(id2owner[member.id])
        if path is not None:
            await interaction.response.send_message(content=None,file=discord.File(path))
        else:
            await interaction.response.send_message("Image generation failed.")
    else:
        await interaction.response.send_message("You are not registered in help.json. Contact to the administrator.")

@tree.command(name="astat", description="create a graph showing how mamy people has participated in VC in one night")
async def sendAllStat(interaction: discord.Interaction, year: int=datetime.datetime.now().year, month: int=datetime.datetime.now().month, day: int=datetime.datetime.now().day):
    stats.botuseLog(id2owner[interaction.user.id])
    path = stats.getOneNightStats(year,month,day)
    if path is not None:
        await interaction.response.send_message(content=None,file=discord.File(path))
    else:
        await interaction.response.send_message("Image generation failed.")

@tree.command(name="calend", description="show the login calender")
async def sendCalend(interaction: discord.Interaction, member: discord.Member=None, year: int=0, month: int=0):
    stats.botuseLog(id2owner[interaction.user.id])
    now = datetime.datetime.now()
    if year==0:
        year=now.year
    if month==0:
        month=now.month
    if member is None:
        member = interaction.user
    path = getCalendar(id2owner[member.id], year, month, False)
    if path is not None:
        await interaction.response.send_message(content=None,file=discord.File(path))
    else:
        await interaction.response.send_message("Image generation failed.")

@tree.command(name="sudo", description="to use this command, administrative privilege required")
@describe(command="shutdown / param / setvcnum")
@describe(param="the value to set")
async def sudo(interaction: discord.Interaction, command: str, param: int=None):
    global vcnum
    if not interaction.user.id in admin_ids:
        await interaction.response.send_message(content="You don't have the privilege", ephemeral=True)
    if command=="shutdown":
        await interaction.response.send_message(content="Bot shutdowned!", ephemeral=True)
        await client.close()
    elif command=="param":
        await interaction.response.send_message(content=f"vcnum:{vcnum}",ephemeral=True)
    elif command=="setvcnum" and param is not None and param > 0:
        vcnum = param

@tree.command(name="config", description="config menu")
async def button(interaction: discord.Interaction):
    await interaction.response.send_message(content="Loading...", ephemeral=True)
    await createConfigView(editor=await interaction.original_response(), owner=id2owner[interaction.user.id])

client.run(os.getenv('TOKEN'))
