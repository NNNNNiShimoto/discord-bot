import discord
import json

#pages: str(path to json) or list[discord.Embed]
async def createPagesView(editor: discord.InteractionMessage, pages: list[discord.Embed]|str):
    try:
        view = PagesView(editor=editor, pages=pages)
    except TypeError as e:
        print(e)
        return None
    await view._init()
    return view

def color(str):
    if str is None:
        return None
    else: return int(str, 16)

#create embeds from path
#To create other pages, follow the data/pages_exp.json from 
def createFromJson(path: str):
    try:
        fp = open(path, encoding="utf-8")
    except FileNotFoundError as e:
        print(e)
        return None, None
    else:
        with fp:
            obj = json.load(fp)
            embeds_list = [ discord.Embed(
                title=emb['title'], 
                description=emb['desc'], 
                color=color(emb['color'])
            ) for emb in obj ]

            file_list = [None]*len(embeds_list)
            for i, embed in enumerate(embeds_list):
                embeds_data = obj[i]

                if embeds_data['author'] is not None:
                    embed.set_author(name=embeds_data['author'])

                if embeds_data['img'] is not None:
                    if embeds_data['img']['path'] is not None:
                        filename = embeds_data['img']['path'].split('/')[-1]
                        file_list[i] = {'path':embeds_data['img']['path'], 'fname':filename}
                        embed.set_image(url='attachment://'+filename)
                    elif embeds_data['img']['url'] is not None:
                        embed.set_image(url=embeds_data['img']['url'])

                if embeds_data['fields'] is not None:        
                    for field in embeds_data['fields']:
                        embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])
                        
        return embeds_list, file_list

class BaseButton(discord.ui.Button['PagesView']):
    def __init__(self, label, disabled=False, style=discord.ButtonStyle.green):
        super().__init__(style=style, label=label, disabled=disabled)

    def createEmbed(self):
        pass        

    def resetButtons(self):
        pass

    def resetPageNumButton(self):
        pageNumButton : BaseButton = self.view.children[len(self.view.children)//2]
        pageNumButton.disabled = True
        pageNumButton.label = str(self.view.page_num+1)+"/"+str(self.view.page_max)

    async def editMessage(self, embed: discord.Embed, interaction: discord.Interaction):
        file_info=self.view.files[self.view.page_num]
        file = []
        if file_info is not None:
            file = [ discord.File(file_info['path'], filename=file_info['fname']) ]
        await self.view.editor.edit(embed=embed, view=self.view, attachments=file)
        try:
            await interaction.response.send_message('')
        except discord.errors.HTTPException:
            pass

    async def callback(self, interaction: discord.Interaction):
        #disable some buttons
        self.resetButtons()

        #load one embed page
        embed = self.createEmbed()

        #disable the page num button
        self.resetPageNumButton()

        #write page
        await self.editMessage(embed, interaction)

#button to move to previous page
class BackButton(BaseButton):
    def createEmbed(self):
        view = self.view
        if view.page_num > 0:
            view.page_num -= 1
        return view.pages[view.page_num]            

    def resetButtons(self):
        view = self.view
        if view.page_num <= 1:
            for button in view.children:
                if type(button) is BackButton or type(button) is RewindButton:
                    button.disabled = True
                else:
                    button.disabled = False
        else:
            for button in view.children:
                button.disabled = False

#button to move to next page
class NextButton(BaseButton):
    def createEmbed(self):
        view = self.view
        if view.page_num+1 < view.page_max:
            view.page_num += 1
        return view.pages[view.page_num]    

    def resetButtons(self):
        view = self.view
        if view.page_num >= view.page_max-2:
            for button in view.children:
                if type(button) is NextButton or type(button) is SkipButton:
                    button.disabled = True
                else:
                    button.disabled = False
        else:
            for button in view.children:
                button.disabled = False

#button to move to the first page
class RewindButton(BaseButton):
    def createEmbed(self):
        view = self.view
        view.page_num = 0
        return view.pages[view.page_num]    

    def resetButtons(self):
        view = self.view
        for button in view.children:
            if type(button) is BackButton or type(button) is RewindButton:
                button.disabled = True
            else:
                button.disabled = False

#button to move to the last page
class SkipButton(BaseButton):
    def createEmbed(self):
        view = self.view
        view.page_num = view.page_max-1
        return view.pages[view.page_num]    

    def resetButtons(self):
        view = self.view
        for button in view.children:
            if type(button) is NextButton or type(button) is SkipButton:
                button.disabled = True
            else:
                button.disabled = False

class PagesView(discord.ui.View):
    def __init__(self, editor: discord.InteractionMessage, pages: list[discord.Embed]|str):
        super().__init__(timeout=None)
        if type(pages) is str:
            self.pages, self.files = createFromJson(pages)
            if self.pages is None or self.files is None:
                raise TypeError('Path name is wrong')
        else:
            self.pages = pages
            self.files = [None]*len(self.pages)
        self.editor = editor
        self.page_num = 0
        self.page_max = len(self.pages)

    async def _init(self):
        if len(self.pages)<2:
            self.add_item(discord.ui.Button(style=discord.ButtonStyle.gray,label='1/'+str(self.page_max), disabled=True))
        elif len(self.pages)==2:
            self.add_item(BackButton(label='◀︎', disabled=True, style=discord.ButtonStyle.green))
            self.add_item(discord.ui.Button(style=discord.ButtonStyle.gray,label='1/'+str(self.page_max), disabled=True))
            self.add_item(NextButton(label='▶︎', disabled=False, style=discord.ButtonStyle.green))
        else:
            self.add_item(RewindButton(label='◀︎◀︎', disabled=True, style=discord.ButtonStyle.blurple))
            self.add_item(BackButton(label='◀︎', disabled=True, style=discord.ButtonStyle.green))
            self.add_item(discord.ui.Button(style=discord.ButtonStyle.gray,label='1/'+str(self.page_max), disabled=True))
            self.add_item(NextButton(label='▶︎', disabled=False, style=discord.ButtonStyle.green))
            self.add_item(SkipButton(label='▶︎▶︎', disabled=False, style=discord.ButtonStyle.blurple))
        
        file=[]
        if self.files[0] is not None:
            file = [ discord.File(self.files[0]['path'], self.files[0]['fname']) ]
        await self.editor.edit(content=None, embed=self.pages[0], view=self, attachments=file)
