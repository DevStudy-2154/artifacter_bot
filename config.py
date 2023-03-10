import os
from dotenv import load_dotenv

load_dotenv()

# 読み込みたい環境変数
BOT_TOKEN = os.getenv('BOT_TOKEN')
