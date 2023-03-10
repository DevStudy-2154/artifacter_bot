# from generateCharacterImage import generater

# if __name__ == "__main__":
#     generater.generation(generater.read_json('data.json'))

import discord
import config

# 必要インスタンス生成
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


# スラッシュコマンド作成
@tree.command(name="test", description="テストコマンド")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("てすと！")


# 起動時のイベント
@client.event
async def on_ready():
    print('起動しました')
    await tree.sync()


client.run(config.BOT_TOKEN)
