import discord
from data.names import id2dispname, admin_ids

async def createMultiRPSGameView(editor: discord.InteractionMessage, id:int, boN: int=1, player_num: int=2):
    try:
        view = MultiRPSGameView(editor=editor, admin=id, boN=boN, player_num=player_num)
    except TypeError as e:
        print(e)
        return None
    await view._init()

class MultiRPSGameView(discord.ui.View):
    def __init__(self, editor: discord.InteractionMessage, admin: int, boN: int=1, player_num: int=2):
        super().__init__(timeout=None)
        self.player_max = player_num
        self.joined_num = 0
        self.player_ids = []
        self.player_wins = [0]*self.player_max
        self.is_pushed = [False]*self.player_max
        self.player_hands = [0]*self.player_max
        self.before_winners = None
        self.draw_num = 0
        self.boN = boN
        self.editor = editor
        self.admin = admin #person's id who can cancel the match
        
    def getWinners(self):
        winners = [id2dispname[self.player_ids[idx]] for idx, win in enumerate(self.player_wins) if win>=self.boN]
        if len(winners)<1:
            return None
        else:
            return ", ".join(map(str, winners))

    def getBeforeWinners(self):
        before_winners = [id2dispname[self.player_ids[idx]] for idx in self.before_winners]
        return ", ".join(map(str, before_winners))
    
    def createWaitingEmbed(self):
        title=f"MultiRPSGame({self.player_max} people, First to {self.boN})"
        desc=""
        for i in range(self.player_max):
            if i < len(self.player_ids):
                desc += f"Player{i+1}: {id2dispname[self.player_ids[i]]}\n"
            else:
                desc += f"Player{i+1}: WAITING...\n"
        return discord.Embed(title=title,description=desc)

    def getIndex(self, id: int):
        for idx, pl_id in enumerate(self.player_ids):
            if pl_id == id:
                return idx
        return -1

    def setRPSGameResult(self):
        hand_set = set(self.player_hands)
        if len(hand_set)==2:
            if hand_set=={0,1}:
                self.before_winners = [idx for idx, hand in enumerate(self.player_hands) if hand == 0]
            elif hand_set=={1,2}:
                self.before_winners = [idx for idx, hand in enumerate(self.player_hands) if hand == 1]
            else:
                self.before_winners = [idx for idx, hand in enumerate(self.player_hands) if hand == 2] 
            for idx in self.before_winners:
                self.player_wins[idx] += 1
            is_draw = False
        else:
            self.draw_num += 1
            is_draw = True
        return is_draw

    async def _init(self):
        self.add_item(JoinButton())
        self.add_item(CancelButton())
        await self.editor.edit(content=None, embed=self.createWaitingEmbed(), view=self)
    
class HandButton(discord.ui.Button['MultiRPSGameView']):
    RPS_LIST =  ["✊", "✌️", "🖐️"]
    def __init__(self, hand):
        super().__init__(style=discord.ButtonStyle.green, label=self.RPS_LIST[hand], disabled=False)
        self.hand = hand
    
    def createEmbed(self):
        view = self.view
        color = None
        title=f"MultiRPSGame({view.player_max} people, First to {view.boN})"
        desc=""
        if view.boN>1:
            desc="============================\n# SCORES\n"
            for i in range(view.player_max):
                if view.player_wins[i] == view.boN-1:
                    desc += f"{id2dispname[view.player_ids[i]]}: :regional_indicator_r::regional_indicator_e::regional_indicator_a::regional_indicator_c::regional_indicator_h:\n"
                    color=0xff0000
                else:
                    desc += f'{id2dispname[view.player_ids[i]]}:{":white_check_mark:"*view.player_wins[i]}\n'
            desc+="============================\n# HANDS\n"
        for i in range(view.player_max):
            if view.is_pushed[i]:
                desc += f"{id2dispname[view.player_ids[i]]}: :white_check_mark:\n"
            else:
                desc += f"{id2dispname[view.player_ids[i]]}: ❓\n"
        if view.boN==1:
            desc += "\n".join(["# DRAW"]*view.draw_num)
        return discord.Embed(title=title, description=desc, color=color)

    async def editMessage(self, interaction: discord.Interaction, err: str):
        await self.view.editor.edit(content=err, embed=self.createEmbed(), view=self.view)
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        idx = view.getIndex(interaction.user.id)
        err_message = None
        if idx < 0:
            err_message = f"{id2dispname[interaction.user.id]}is not a player"
        else:
            if view.is_pushed[idx]:
                err_message = f"{id2dispname[interaction.user.id]} has already made the choice"
            else:
                view.player_hands[idx] = self.hand
                view.is_pushed[idx] = True
        
        if all(view.is_pushed):
            view.clear_items()
            view.add_item(ResultButton())

        await self.editMessage(interaction, err_message)

class JoinButton(discord.ui.Button['MultiRPSGameView']):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="JOIN", disabled=False)

    async def editMessage(self, inter: discord.Interaction, err: str):
        await self.view.editor.edit(content=err, embed=self.view.createWaitingEmbed(), view=self.view)
        try:
            await inter.response.send_message('')
        except discord.errors.HTTPException:
            pass

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        err_message = None
        if view.player_max > view.joined_num:
            if interaction.user.id in view.player_ids:
                err_message = f"{id2dispname[interaction.user.id]} has already joined"
            else:
                view.player_ids.append(interaction.user.id)
                view.joined_num += 1
        else:
            err_message = f"Maximum number of people has been reached."

        if view.player_max == view.joined_num:
            view.clear_items()
            view.add_item(StartButton())
            view.add_item(CancelButton())

        await self.editMessage(inter=interaction, err=err_message)

class StartButton(discord.ui.Button['MultiRPSGameView']):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Start!", disabled=False)

    def createFirstEmbed(self):
        view = self.view
        title=f"MultiRPSGame({view.player_max} people, First to {view.boN})"
        desc=""
        if view.boN>1:
            desc="============================\n# SCORES\n"
            for i in range(view.player_max):
                desc += f'{id2dispname[view.player_ids[i]]}:{":white_check_mark:"*view.player_wins[i]}\n'
            desc+="============================\n# HANDS\n"
        for i in range(view.player_max):
            desc += f"{id2dispname[view.player_ids[i]]}: ❓\n"
        return discord.Embed(title=title, description=desc)

    async def editMessage(self, interaction: discord.Interaction):
        await self.view.editor.edit(content=None, embed=self.createFirstEmbed(), view=self.view)
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        view.clear_items()
        view.add_item(HandButton(0))
        view.add_item(HandButton(2))
        view.add_item(HandButton(1))
        await self.editMessage(interaction)

class ResultButton(discord.ui.Button['MultiRPSGameView']):
    RPS_LIST = ["✊", "✌️", "🖐️"]
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Fight!", disabled=False)

    def createResultEmbed(self):
        view = self.view
        title=f"MultiRPSGame({view.player_max} people, First to {view.boN})"
        desc = ""

        if view.boN == 1:
            desc+= f"# {view.getWinners()} VICTORY!\n"
            for i in range(view.player_max):
                desc+= f"{id2dispname[view.player_ids[i]]}: {self.RPS_LIST[view.player_hands[i]]}\n"
            color= 0xffd700
            return discord.Embed(title=title, description=desc, color=color), True

        winners = view.getWinners()
        if winners is not None: #Someone Wins
            desc+= f"# {winners} VICTORY!\n"
            desc+="============================\n# SCORES\n"
            for i in range(view.player_max):
                desc += f'{id2dispname[view.player_ids[i]]}:{":white_check_mark:"*view.player_wins[i]}\n'
            desc+="============================\n# LAST HANDS\n"
            for i in range(view.player_max):
                desc+= f"{id2dispname[view.player_ids[i]]}: {self.RPS_LIST[view.player_hands[i]]}\n"
            color= 0xffd700
            return discord.Embed(title=title, description=desc, color=color), True
        
        else: #continue match
            color=None
            desc="============================\n# SCORES\n"
            for i in range(view.player_max):
                if view.player_wins[i] == view.boN-1:
                    desc += f"{id2dispname[view.player_ids[i]]}: :regional_indicator_r::regional_indicator_e::regional_indicator_a::regional_indicator_c::regional_indicator_h:\n"
                    color=0xff0000
                else:
                    desc += f'{id2dispname[view.player_ids[i]]}:{":white_check_mark:"*view.player_wins[i]}\n'
            desc+=f"============================\n# {view.getBeforeWinners()} WIN!\n"
            for i in range(view.player_max):
                desc+= f"{id2dispname[view.player_ids[i]]}: {self.RPS_LIST[view.player_hands[i]]}\n"

            return discord.Embed(title=title, description=desc, color=color), False

    def createDrawEmbed(self):
        view = self.view
        title=f"MultiRPSGame({view.player_max} people, First to {view.boN})"
        color=None
        desc=""
        if self.view.boN>1:
            color=0x330000 * min(view.draw_num,5)
            desc="============================\n# SCORES\n"
            for i in range(view.player_max):
                if view.player_wins[i] == view.boN-1:
                    desc += f"{id2dispname[view.player_ids[i]]}: :regional_indicator_r::regional_indicator_e::regional_indicator_a::regional_indicator_c::regional_indicator_h:\n"
                    color=0xff0000
                else:
                    desc += f'{id2dispname[view.player_ids[i]]}:{":white_check_mark:"*view.player_wins[i]}\n'
            desc+="============================\n# DRAW\n"
            for i in range(view.player_max):
                desc += f"{id2dispname[view.player_ids[i]]}: {self.RPS_LIST[view.player_hands[i]]}\n"
        else:
            for i in range(view.player_max):
                desc += f"{id2dispname[view.player_ids[i]]}: {self.RPS_LIST[view.player_hands[i]]}\n"
            desc += "\n".join(["# DRAW"]*view.draw_num)
            color=0x330000 * min(view.draw_num,5)

        return discord.Embed(title=title, description=desc, color=color)

    async def editMessage(self, interaction: discord.Interaction):
        if self.isDraw:
            await self.view.editor.edit(content=None, embed=self.createDrawEmbed(), view=self.view)
        else:
            emb, isFinished = self.createResultEmbed()
            if isFinished:
                await self.view.editor.edit(content=None, embed=emb, view=None)
            else:
                await self.view.editor.edit(content=None, embed=emb, view=self.view)
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        self.isDraw = view.setRPSGameResult()
        if self.isDraw:
            view.clear_items()
            view.add_item(HandButton(0))
            view.add_item(HandButton(2))
            view.add_item(HandButton(1))
            view.is_pushed = [False]*view.player_max
        else:
            view.clear_items()
            view.add_item(NextButton())
        await self.editMessage(interaction)

class NextButton(discord.ui.Button['MultiRPSGameView']):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label="Next", disabled=False)

    def resetButtons(self):
        self.view.clear_items()
        self.view.add_item(HandButton(0))
        self.view.add_item(HandButton(2))
        self.view.add_item(HandButton(1))

    def createPrepareEmbed(self):
        view = self.view
        title=f"MultiRPSGame({view.player_max} people, First to {view.boN})"
        color=None
        desc="============================\n# SCORES\n"
        for i in range(view.player_max):
            if view.player_wins[i] == view.boN-1:
                desc += f"{id2dispname[view.player_ids[i]]}: :regional_indicator_r::regional_indicator_e::regional_indicator_a::regional_indicator_c::regional_indicator_h:\n"
                color=0xff0000
            else:
                desc += f'{id2dispname[view.player_ids[i]]}:{":white_check_mark:"*view.player_wins[i]}\n'
        desc+="============================\n# HANDS\n"
        for i in range(view.player_max):
            desc += f"{id2dispname[view.player_ids[i]]}: ❓\n"
        return discord.Embed(title=title, description=desc, color=color)

    async def callback(self, interaction: discord.Interaction):
        self.view.draw_num = 0
        self.view.is_pushed = [False]*self.view.player_max
        self.resetButtons()
        await self.view.editor.edit(embed=self.createPrepareEmbed(), view=self.view)
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass

class CancelButton(discord.ui.Button['MultiRPSGameView']):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label="Cancel", disabled=False)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.view.admin or interaction.user.id in admin_ids:
            await self.view.editor.edit(content=None, embed=discord.Embed(title="The match has been canceled."), view=None)
        else:
            await self.view.editor.edit(content="Only command user can cancel the match")
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass
        