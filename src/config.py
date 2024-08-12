import json
import discord
from data.names import is_join_list, owner2id, id2dispname

#config.json
#notice int: how many people enter the call and send notifications when they do
#        0: disabled
#       -1: each join
#     oths: number of people
#
#is_noticed bool: if bot sended notifications in recent time
#
#device_id int|None : which account bot will send notifications
#       id:id

def readOneData(type: str, owner: str) -> int:
    """
    Args:
        type str: see config.json. "notice" or "is_noticed" or "device_id"
        owner str: owner name

    Returns:
        int: config value
    """
    with open("data/config.json",'r') as f:
        jobj = json.load(f)
        return jobj[type][owner]

def readOneConfig(type: str) -> dict:
    with open("data/config.json",'r') as f:
        jobj = json.load(f)
        return jobj[type]

def writeOneData(type: str, owner: str, data: int|bool):
    with open("data/config.json",'r') as f:
        jobj = json.load(f)
        jobj[type][owner] = data

    with open("data/config.json",'w') as g:
        json.dump(jobj, g, indent=4)

def writeOneConfig(type: str, data: dict):
    with open("data/config.json",'r') as f:
        jobj = json.load(f)
        jobj[type] = data

    with open("data/config.json",'w') as g:
        json.dump(jobj, g, indent=4)

async def createConfigView(editor: discord.InteractionMessage, owner: str):
    try:
        view = ConfigView(editor=editor, owner=owner)
    except TypeError as e:
        print(e)
        return None
    await view._init()

class ConfigView(discord.ui.View):
    def __init__(self, editor: discord.InteractionMessage, owner: str):
        super().__init__(timeout=120)
        self.editor = editor
        self.owner = owner
        self.config_view=[
            NoticeConfig(),
            NoticeDeviceConfig(self.owner)
        ]

    def createFirstEmbed(self):
        notice_val = readOneData("notice", self.owner)
        title = "CONFIG" 
        if notice_val == 0:
            desc="### Number of people to send notifications\n Current:Disabled"
            return discord.Embed(title=title, description=desc)
        else: 
            if notice_val < 0:
                num_conf="Notify each time a person joins"
            else:
                num_conf=f"Notify when {notice_val} or more people join"
            
            device_id = readOneData("device_id", self.owner)
            if device_id is None:
                device_conf="None"
            else:
                device_conf=id2dispname[device_id]
            desc=f"### Number of people to send notifications\n Current:{num_conf}\n### Which to notify\n Current:{device_conf}"
            return discord.Embed(title=title, description=desc)

    async def showControlPanel(self):
        notice_val = readOneData("notice", self.owner)
        self.clear_items()
        self.add_item(self.config_view[0])
        if notice_val!=0:
            self.add_item(self.config_view[1])
        #add "<" or ">" buttons if more config menu
        await self.editor.edit(content=None, embed=self.createFirstEmbed(), view=self)

    async def _init(self):
        notice_val = readOneData("notice", self.owner)
        self.add_item(self.config_view[0])
        if notice_val!=0:
            self.add_item(self.config_view[1])
        #add "<" or ">" buttons if more config menu
        await self.editor.edit(content=None, embed=self.createFirstEmbed(), view=self)

class ExclusiveSelect(discord.ui.Select['ConfigView']):
    def __init__(self, placeholder: str, options: list[discord.SelectOption], max_values=1, disabled=False):
        super().__init__(placeholder=placeholder, min_values=1, max_values=max_values, options=options, disabled=disabled)

    async def callback(self, interaction: discord.Interaction):
        pass

class NoticeConfig(ExclusiveSelect):
    def __init__(self):
        options = [
            discord.SelectOption(label='Disabled', description='No notification'),
            discord.SelectOption(label='1personJoin')
        ]
        options += [discord.SelectOption(label=f'{i+2}peopleJoin') for i in range(len(owner2id)-2)]

        options.append(discord.SelectOption(label='EachJoin', description='Deprecated:Notify each time a person joins.'))

        super().__init__(placeholder="When is the notification sent?", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0]=='Disabled':
            writeOneData("notice", self.view.owner, 0)
        elif self.values[0]=='EachJoin':
            writeOneData("notice", self.view.owner, -1)
        else:
            writeOneData("notice", self.view.owner, int(self.values[0][0]))
        await self.view.showControlPanel()
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass

class NoticeDeviceConfig(ExclusiveSelect):
    def __init__(self, owner: str):
        self.owner = owner
        self.name_id_dict = {id2dispname[id] : id for id in owner2id[owner]}
        options = [discord.SelectOption(label=name) for name in self.name_id_dict.keys()]
        super().__init__(placeholder="Which to send notifications?", options=options, disabled=len(self.name_id_dict)<=1)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] in self.name_id_dict:
            writeOneData("device_id", self.owner, self.name_id_dict[self.values[0]])
        else:
            print("error: undefined in config.json")
        await self.view.showControlPanel()
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass

#called when a person joined VC
#return id list to whose account bot send notifications
def getNoticeIDList(vcnum: int) -> list[int]:
    notice_config = readOneConfig("notice")
    is_noticed = readOneConfig("is_noticed")
    device_id = readOneConfig("device_id")
    join_owner = [owner for owner in is_join_list.keys() if is_join_list[owner]]
    notice_ids = []
    for owner in list(notice_config.keys()):
        if notice_config[owner] < 0 and not owner in join_owner: # everytime notice
            id = device_id[owner]
            if id is not None:
                notice_ids.append(id)
        elif notice_config[owner]==0: # never notice
            pass
        elif not owner in join_owner and not is_noticed[owner]:
            if notice_config[owner] <= vcnum:
                id = device_id[owner]
                if id is not None:
                    notice_ids.append(id)
                writeOneData("is_noticed", owner, True)
    return notice_ids

#called when all of VCs is closed
#reset is_noticed
def resetIsNoticed():
    is_noticed = readOneConfig("is_noticed")
    for ini in is_noticed.keys():
        is_noticed[ini] = False
    writeOneConfig("is_noticed", is_noticed)