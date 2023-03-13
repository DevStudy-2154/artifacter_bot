import requests
import json
import os
from lib import common


damage = {
    "炎": {"name": "炎元素ダメージ", "prop": "40"},
    "雷": {"name": "雷元素ダメージ", "prop": "41"},
    "水": {"name": "水元素ダメージ", "prop": "42"},
    "草": {"name": "草元素ダメージ", "prop": "43"},
    "風": {"name": "風元素ダメージ", "prop": "44"},
    "岩": {"name": "岩元素ダメージ", "prop": "45"},
    "氷": {"name": "氷元素ダメージ", "prop": "46"},
}


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


# キャラ情報作成
def createCharacterData(data, id):
    cwd = os.path.dirname(os.path.abspath(__file__))
    jpData = common.read_json(f'{cwd}/loc.json')['ja']
    charactersData = common.read_json(f'{cwd}/characters.json')
    reliquaryData = common.read_json(f'{cwd}/reliquary.json')

    apiData = data['nodes'][1]['data']
    characterInfo = apiData[int(id)]

    jsonAvatarId = characterInfo['avatarId']
    avatarId = str(apiData[jsonAvatarId])
    nameTextMapHash = str(charactersData[avatarId]['NameTextMapHash'])
    characterName = jpData[nameTextMapHash]

    # レベル, 好感度, 凸
    levelId = apiData[characterInfo['propMap']]['4001']
    loveId = apiData[characterInfo['fetterInfo']]['expLevel']
    const = len(apiData[characterInfo['talentIdList']]) if 'talentIdList' in characterInfo else 0

    # 元素
    jsonAvatarId = characterInfo['avatarId']
    avatarId = str(apiData[jsonAvatarId])
    element = reliquaryData[charactersData[avatarId]['Element']]

    # キャラクターステータス
    status = apiData[characterInfo['fightPropMap']]
    totalHPId = status['2000']
    totalAttackId = status['2001']
    totalDefenseId = status['2002']
    familiarityId = status['28']
    criticalRateId = status['20']
    criticalDamageId = status['22']
    chargeId = status['23']
    skill = apiData[characterInfo['skillLevelMap']]
    baseHPId = status['1']
    baseAttackId = status['4']
    baseDefenseId = status['7']
    elementDamageId = status[damage[element]["prop"]]

    equipList = apiData[characterInfo['equipList']]

    # 武器
    weaponProp = apiData[apiData[equipList[-1]]['weapon']]
    weaponDetail = apiData[apiData[equipList[-1]]['flat']]
    weaponName = apiData[weaponDetail['nameTextMapHash']]
    weaponTotu = list(apiData[weaponProp['affixMap']].values())[0]
    weaponReality = apiData[weaponDetail['rankLevel']]
    weaponBaseAtk = apiData[apiData[apiData[weaponDetail['weaponStats']][0]]['statValue']]
    weaponSubStatus = jpData[apiData[apiData[apiData[weaponDetail['weaponStats']][1]]['appendPropId']]]
    weaponSubStatusValue = apiData[apiData[apiData[weaponDetail['weaponStats']][1]]['statValue']]

    # 聖遺物
    reliquaries = {}
    reliquariesScore = {}
    totalScore = 0
    for index in range(len(equipList)):

        # 武器情報になったらストップ
        if index == len(equipList)-1:
            break

        reliquaryProp = apiData[apiData[equipList[index]]['flat']]
        reliquaryName = apiData[reliquaryProp['setNameTextMapHash']]
        reliquaryLevel = apiData[apiData[apiData[equipList[index]]['reliquary']]['level']] - 1
        reliquaryRank = apiData[reliquaryProp['rankLevel']]
        reliquaryType = reliquaryData[apiData[reliquaryProp['equipType']]]

        # メインステータス
        reliquaryMainStatus = apiData[apiData[reliquaryProp['reliquaryMainstat']]['mainPropId']]
        reliquaryMainStatusValue = apiData[apiData[reliquaryProp['reliquaryMainstat']]['statValue']]

        # サブステータス
        subStatuses = []
        reliquarySubStatusList = apiData[reliquaryProp['reliquarySubstats']]
        score = 0

        for subStatus in reliquarySubStatusList:
            subStatusName = reliquaryData[apiData[apiData[subStatus]['appendPropId']]]
            subStatusValue = apiData[apiData[subStatus]['statValue']]
            status = {"option": subStatusName, "value": subStatusValue}
            subStatuses.append(status)

            # スコア計算
            if subStatusName == "会心率":
                score += subStatusValue * 2
            elif subStatusName == "会心ダメージ" or subStatusName == "攻撃パーセンテージ":
                score += subStatusValue

        score = round(score, 1)
        totalScore += score
        reliquariesScore[reliquaryType] = score

        reliquaries[reliquaryType] = {
            "type": jpData[reliquaryName],
            "Level": reliquaryLevel,
            "rarelity": reliquaryRank,
            "main": {
                "option": reliquaryData[reliquaryMainStatus],
                "value": reliquaryMainStatusValue
            },
            "sub": subStatuses
        }

    jsonData = {
        "Character": {
            "Name": characterName,
            "Const": const,
            "Level": int(apiData[apiData[levelId]['val']]),
            "Love": apiData[loveId],
            "Status": {
                "HP": round(apiData[totalHPId]),
                "攻撃力": round(apiData[totalAttackId]),
                "防御力": round(apiData[totalDefenseId]),
                "元素熟知": round(apiData[familiarityId]),
                "会心率": round(apiData[criticalRateId]*100, 1),
                "会心ダメージ": round(apiData[criticalDamageId]*100, 1),
                "元素チャージ効率": round(apiData[chargeId]*100, 1),
                damage[element]["name"]: round(apiData[elementDamageId]*100, 1),
            },
            "Talent": {
                "通常": apiData[list(skill.values())[0]],
                "スキル": apiData[list(skill.values())[1]],
                "爆発": apiData[list(skill.values())[2]],
            },
            "Base":{
                "HP": round(apiData[baseHPId]),
                "攻撃力": round(apiData[baseAttackId]),
                "防御力": round(apiData[baseDefenseId]),
            }
        },
        "Weapon": {
            "name": jpData[weaponName],
            "Level": apiData[weaponProp['level']],
            "totu": apiData[weaponTotu]+1,
            "rarelity": weaponReality,
            "BaseATK": weaponBaseAtk,
            "Sub": {
                "name": weaponSubStatus,
                "value": str(weaponSubStatusValue)
            }
        },
        "Score": {
            "State": "HP",
            "total": round(totalScore, 1),
            "flower": reliquariesScore['flower'],
            "wing": reliquariesScore['wing'],
            "clock": reliquariesScore['clock'],
            "cup": reliquariesScore['cup'],
            "crown": reliquariesScore['crown'],
        },
        "Artifacts": reliquaries,
        "元素": element
    }

    return jsonData


# キャラ名を整形して返す
def getName(uid):
    data = getApi(uid)
    characters = translatedName(data)

    return characters


# キャラクターデータをjson形式にして返す
def getCharacterData(id, uid):
    data = getApi(uid)
    return createCharacterData(data, id)
