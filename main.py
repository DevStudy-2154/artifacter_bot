import config
import discord
from discord.ui import Select, View
from generateCharacterImage import generater
from lib import common
from enkaNetwork import enka


# 必要インスタンス生成
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


# セレクトボックス
class CharactersListView(View):
    def __init__(self, characters, uid):
        super().__init__()
        self.add_item(CharactersListSelect(characters, uid))

        # options = []
        # for character in characters:
        #     options.append(discord.SelectOption(label=character['name'], value=character['id']))

    # # 選択された後の処理
    # @discord.ui.select(placeholder="表示させたいキャラを選んでください", min_values=1, max_values=1, options=options)
    # async def callback(self, select, interaction: discord.Interaction):
    #     select.disabled = True
    #     await interaction.response.edit_message(view=self)
    #     await interaction.response.send_message(f'{interaction.user.name}は{select.values[0]}を選択しました', ephemeral=True)
    #     # generater.generation(common.read_json('data.json'))


# セレクトボックスの処理
class CharactersListSelect(Select):
    def __init__(self, characters, uid):
        self.uid = uid

        options = []
        for character in characters:
            options.append(discord.SelectOption(label=character['name'], value=character['id']))

        super().__init__(placeholder="表示させたいキャラを選んでください", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # self.disabled = True
        # await interaction.response.edit_message(view=interaction)
        # await interaction.response.send_message(f'{interaction.user.name}は{self.values[0]}を選択しました', ephemeral=True)
        data = enka.getCharacterData(self.values[0], self.uid)
        generater.generation(data)


# スラッシュコマンド作成
@tree.command(name="build", description="キャラ画像生成")
async def build_command(interaction: discord.Interaction, uid:int):
    characters = enka.getName(uid)
    await interaction.response.send_message("表示させたいキャラを選んでください", view=CharactersListView(characters, uid), ephemeral=True)


# 起動時のイベント
@client.event
async def on_ready():
    print('起動しました')
    await tree.sync()


client.run(config.BOT_TOKEN)
