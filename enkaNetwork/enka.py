import requests
import json
import os
from lib import common


# enka networkからキャラ情報取得
def getApi(uid):
    response = requests.get(f"https://enka.network/u/{uid}/__data.json")
    data = response.json()

    return data


# キャラ名を日本語に置き換え
def translatedName(data):
    cwd = os.path.dirname(os.path.abspath(__file__))
    jpData = common.read_json(f'{cwd}/loc.json')['ja']
    charactersData = common.read_json(f'{cwd}/characters.json')

    apiData = data['nodes'][1]['data']
    avatarInfoList = apiData[0]['avatarInfoList'] # 29 = [30, 227, 378, 505, 624, 741],

    # キャラクター名とIDを格納
    characters = []
    for character in apiData[avatarInfoList]:
        jsonAvatarId = apiData[character]['avatarId']
        avatarId = str(apiData[jsonAvatarId])
        nameTextMapHash = str(charactersData[avatarId]['NameTextMapHash'])
        characterName = jpData[nameTextMapHash]
        characters.append({ 'id': character, 'name': characterName })

    return characters


# キャラ名を整形して返す
def getName(uid):
    data = getApi(uid)
    characters = translatedName(data)

    return characters
