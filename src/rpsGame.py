import discord
import random

async def createRPSGameView(editor: discord.InteractionMessage, boN: int=1):
    try:
        view = RPSGameView(editor=editor, boN=boN)
    except TypeError as e:
        print(e)
        return None
    await view._init()

class RPSGameView(discord.ui.View):
    def __init__(self, editor: discord.InteractionMessage, boN: int=1):
        super().__init__(timeout=None)
        self.drawnum = 0
        self.plWins = 0
        self.cpWins = 0
        self.boN = boN
        self.editor = editor

    async def _init(self):
        self.add_item(HandButton(0))
        self.add_item(HandButton(2))
        self.add_item(HandButton(1))
        await self.editor.edit(content=None, embed=discord.Embed(title="🤖❓vs❓YOU"), view=self)

class HandButton(discord.ui.Button['RPSGameView']):
    RPS_LIST =  ["✊", "✌️", "🖐️"]
    def __init__(self, plHand):
        super().__init__(style=discord.ButtonStyle.green, label=self.RPS_LIST[plHand], disabled=False)
        self.plHand = plHand
        self.cpHand = 0
        self.result = 3
        # 0:draw, 1: player WIN, 2:player LOSE
    
    def setRPSGameResult(self):
        self.cpHand = random.randrange(3)
        self.result = (self.cpHand-self.plHand)%3
        if self.result==0:
            self.view.drawnum+=1
        elif self.result==1:
            self.view.plWins+=1
        elif self.result==2:
            self.view.cpWins+=1

    def createResultEmbed(self):
        view = self.view
        title = f"🤖{self.RPS_LIST[self.cpHand]}vs{self.RPS_LIST[self.plHand]}YOU"
        score = f'============================\nYOU:{":white_check_mark:"*view.plWins}\nCPU:{":white_check_mark:"*view.cpWins}\n============================'
        if self.result==0:# draw
            color = 0x330000 * min(view.drawnum, 5)
            if view.boN == 1:
                desc = "# DRAW \n" * view.drawnum
            else:
                desc = "# DRAW \n" * view.drawnum + score
        elif self.result==1: #player win
            if view.boN == 1:
                draws = "\n".join(["# DRAW"]*view.drawnum)
                desc = f'{draws}\n# YOU WIN \n'
                color=0x00ff00
            elif view.boN <= view.plWins:
                if view.cpWins==0 and view.boN>1:
                    desc=f"# PERFECT! \n{score}"
                else: desc = f"# YOU WIN \n{score}"
                color=0x00ff00
            else: 
                draws = "\n".join(["# DRAW"]*view.drawnum)
                desc = f'{draws}\n# YOU WIN \n{score}'
                color=None
        else: #player lose
            if view.boN == 1:
                draws = "\n".join(["# DRAW"]*view.drawnum)
                desc = f'{draws}\n# YOU LOSE \n'
                color=0xff0000
            elif view.boN <= view.cpWins:
                if view.plWins==0 and view.boN>1:
                    desc=f"# CRUSHING... \n{score}"
                else: desc = f"# YOU LOSE \n{score}"
                color=0xff0000
            else: 
                draws = "\n".join(["# DRAW"]*view.drawnum)
                desc = f'{draws}\n# YOU LOSE \n{score}'
                color=None
        return discord.Embed(title=title, description=desc, color=color)

    def resetButtons(self):
        if self.result==0: #draw
            pass
        elif self.view.boN==1 or self.view.boN<= self.view.plWins or self.view.boN<= self.view.cpWins:
            self.view.clear_items()
        else:
            self.view.clear_items()
            self.view.add_item(NextButton())
    
    async def showResult(self, interaction: discord.Interaction, embed: discord.Embed):
        self.resetButtons()
        await self.view.editor.edit(embed=embed, view=self.view)
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass

    async def callback(self, interaction: discord.Interaction):
        self.setRPSGameResult()
        emb = self.createResultEmbed()
        await self.showResult(interaction, emb)

class NextButton(discord.ui.Button['RPSGameView']):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label="Next", disabled=False)

    def resetButtons(self):
        self.view.clear_items()
        self.view.add_item(HandButton(0))
        self.view.add_item(HandButton(2))
        self.view.add_item(HandButton(1))

    def createEmbed(self):
        desc = f'============================\nYOU:{":white_check_mark:"*self.view.plWins}\nCPU:{":white_check_mark:"*self.view.cpWins}\n============================'
        return discord.Embed(title="🤖❓vs❓YOU",description=desc)

    async def callback(self, interaction: discord.Interaction):
        self.view.drawnum=0
        self.resetButtons()
        await self.view.editor.edit(embed=self.createEmbed(), view=self.view)
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass
