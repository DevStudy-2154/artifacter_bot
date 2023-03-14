import config
import os
import discord
from discord.ui import Select, View
from generateCharacterImage import generater
from enkaNetwork import enka


cwd = os.path.dirname(os.path.abspath(__file__))


# 必要インスタンス生成
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


# セレクトボックス
class CharactersListView(View):
    def __init__(self, characters, uid):
        super().__init__()
        self.add_item(CharactersListSelect(characters, uid))


# セレクトボックスの処理
class CharactersListSelect(Select):
    def __init__(self, characters, uid):
        self.uid = uid

        options = []
        for character in characters:
            options.append(discord.SelectOption(label=character['name'], value=character['id']))

        super().__init__(placeholder="表示させたいキャラを選んでください", min_values=1, max_values=1, options=options)

    # 選択後の処理
    async def callback(self, interaction: discord.Interaction):
        # self.disabled = True
        data = enka.get_character_data(self.values[0], self.uid)
        image = generater.generation(data)
        path = f'{cwd}/generateCharacterImage/image/{image}'

        await interaction.response.defer(ephemeral = True)
        await interaction.followup.send(file=discord.File(path))

        # 画像削除
        os.remove(path)


# スラッシュコマンド作成
# キャラクター画像生成コマンド
@tree.command(name="build", description="キャラ画像生成")
async def build_command(interaction: discord.Interaction, uid:int):
    characters = enka.get_my_characters(uid)
    await interaction.response.send_message("表示させたいキャラを選んでください", view=CharactersListView(characters, uid), ephemeral=True)


# 起動時のイベント
@client.event
async def on_ready():
    print('起動しました')
    await tree.sync()


client.run(config.BOT_TOKEN)
