import requests
import os
from lib import common


cwd = os.path.dirname(os.path.abspath(__file__))
jp_data = common.read_json(f'{cwd}/jp.json')
characters_data = common.read_json(f'{cwd}/characters.json')


# 元素名からダメージ名とAPI IDへの対応付け
element_to_damage = {
    "炎": {"name": "炎元素ダメージ", "prop": "40"},
    "雷": {"name": "雷元素ダメージ", "prop": "41"},
    "水": {"name": "水元素ダメージ", "prop": "42"},
    "草": {"name": "草元素ダメージ", "prop": "43"},
    "風": {"name": "風元素ダメージ", "prop": "44"},
    "岩": {"name": "岩元素ダメージ", "prop": "45"},
    "氷": {"name": "氷元素ダメージ", "prop": "46"},
}


# enka networkからキャラ情報取得
def get_api(uid):
    response = requests.get(f"https://enka.network/u/{uid}/__data.json")
    data = response.json()

    return data


# キャラ名（日本語）の取得
def get_jp_name(id, data):
    avatarId = get_avatarId(id, data)
    hash = str(characters_data[avatarId]['NameTextMapHash'])
    name = jp_data[hash]

    return name


# キャラクター情報上のアバターIDの取得
def get_avatarId(id, data):
    json_avatarId = data[int(id)]['avatarId']
    avatarId = str(data[json_avatarId])

    return avatarId


# キャラ名を日本語に置き換え
def tlanslated_to_jp(data):
    api_data = data['nodes'][1]['data']
    avatar_infolist = api_data[0]['avatarInfoList']

    # キャラクター名とAPIデータ上のIDを格納
    my_characters = []
    for character in api_data[avatar_infolist]:
        name = get_jp_name(character, api_data)
        my_characters.append({ 'id': character, 'name': name })

    return my_characters


# キャラ情報作成
def create_character_data(data, id):
    api_data = data['nodes'][1]['data']
    character_info = api_data[int(id)]  # 該当キャラクターの情報が格納
    avatarId = get_avatarId(id, api_data)

    # レベル, 好感度, 凸, 元素
    levelId = api_data[character_info['propMap']]['4001']
    level = int(api_data[api_data[levelId]['val']])
    love = api_data[api_data[character_info['fetterInfo']]['expLevel']]
    totu = len(api_data[character_info['talentIdList']]) if 'talentIdList' in character_info else 0
    element = jp_data[characters_data[avatarId]['Element']]

    # キャラクターステータス
    status = api_data[character_info['fightPropMap']]  # 該当キャラクターのステータスが格納
    total_HP = round(api_data[status['2000']])
    total_attack = round(api_data[status['2001']])
    total_defense = round(api_data[status['2002']])
    jukuchi = round(api_data[status['28']])
    critical_rate = round(api_data[status['20']]*100, 1)
    critical_damage = round(api_data[status['22']]*100, 1)
    element_charge = round(api_data[status['23']]*100, 1)
    element_damage = round(api_data[status[element_to_damage[element]["prop"]]]*100, 1)

    skill = api_data[character_info['skillLevelMap']]

    base_HP = round(api_data[status['1']])
    base_attack = round(api_data[status['4']])
    base_defense = round(api_data[status['7']])

    equiplist = api_data[character_info['equipList']]  #

    # 武器
    weapon_prop = api_data[api_data[equiplist[-1]]['weapon']]
    weapon_detail = api_data[api_data[equiplist[-1]]['flat']]
    weapon_name = api_data[weapon_detail['nameTextMapHash']]
    weapon_level = api_data[weapon_prop['level']]
    weapon_totu = api_data[list(api_data[weapon_prop['affixMap']].values())[0]]+1
    weapon_reality = api_data[weapon_detail['rankLevel']]
    weapon_base_atk = api_data[api_data[api_data[weapon_detail['weaponStats']][0]]['statValue']]
    weapon_sub_status = jp_data[api_data[api_data[api_data[weapon_detail['weaponStats']][1]]['appendPropId']]]
    weapon_sub_status_value = api_data[api_data[api_data[weapon_detail['weaponStats']][1]]['statValue']]

    # 聖遺物
    reliquaries = {}  # 各聖遺物情報
    reliquaries_score = {}  # 各聖遺物のスコア
    total_score = 0
    for index in range(len(equiplist)):

        # 武器情報になったら処理を止める
        if index == len(equiplist)-1:
            break

        reliquary_prop = api_data[api_data[equiplist[index]]['flat']]
        reliquary_name = api_data[reliquary_prop['setNameTextMapHash']]
        reliquary_level = api_data[api_data[api_data[equiplist[index]]['reliquary']]['level']] - 1
        reliquary_rank = api_data[reliquary_prop['rankLevel']]
        reliquary_type = jp_data[api_data[reliquary_prop['equipType']]]

        # メインステータス
        reliquary_main_status = api_data[api_data[reliquary_prop['reliquaryMainstat']]['mainPropId']]
        reliquary_main_status_value = api_data[api_data[reliquary_prop['reliquaryMainstat']]['statValue']]

        # サブステータス
        sub_statuses = []
        reliquary_sub_statuslist = api_data[reliquary_prop['reliquarySubstats']]
        score = 0

        for sub_status in reliquary_sub_statuslist:
            sub_status_name = jp_data[api_data[api_data[sub_status]['appendPropId']]]
            sub_status_value = api_data[api_data[sub_status]['statValue']]
            status = {"option": sub_status_name, "value": sub_status_value}
            sub_statuses.append(status)

            # スコア計算
            if sub_status_name == "会心率":
                score += sub_status_value * 2
            elif sub_status_name == "会心ダメージ" or sub_status_name == "攻撃パーセンテージ":
                score += sub_status_value

        score = round(score, 1)
        total_score += score
        reliquaries_score[reliquary_type] = score

        reliquaries[reliquary_type] = {
            "type": jp_data[reliquary_name],
            "Level": reliquary_level,
            "rarelity": reliquary_rank,
            "main": {
                "option": jp_data[reliquary_main_status],
                "value": reliquary_main_status_value
            },
            "sub": sub_statuses
        }

    jsonData = {
        "Character": {
            "Name": get_jp_name(id, api_data),
            "Const": totu,
            "Level": level,
            "Love": love,
            "Status": {
                "HP": total_HP,
                "攻撃力": total_attack,
                "防御力": total_defense,
                "元素熟知": jukuchi,
                "会心率": critical_rate,
                "会心ダメージ": critical_damage,
                "元素チャージ効率": element_charge,
                element_to_damage[element]["name"]: element_damage,
            },
            "Talent": {
                "通常": api_data[list(skill.values())[0]],
                "スキル": api_data[list(skill.values())[1]],
                "爆発": api_data[list(skill.values())[2]],
            },
            "Base":{
                "HP": base_HP,
                "攻撃力": base_attack,
                "防御力": base_defense,
            }
        },
        "Weapon": {
            "name": jp_data[weapon_name],
            "Level": weapon_level,
            "totu": weapon_totu,
            "rarelity": weapon_reality,
            "BaseATK": weapon_base_atk,
            "Sub": {
                "name": weapon_sub_status,
                "value": str(weapon_sub_status_value)
            }
        },
        "Score": {
            "State": "HP",
            "total": round(total_score, 1),
            "flower": reliquaries_score['flower'],
            "wing": reliquaries_score['wing'],
            "clock": reliquaries_score['clock'],
            "cup": reliquaries_score['cup'],
            "crown": reliquaries_score['crown'],
        },
        "Artifacts": reliquaries,
        "元素": element
    }

    return jsonData


# キャラ名を整形して返す
def get_my_characters(uid):
    data = get_api(uid)
    characters = tlanslated_to_jp(data)

    return characters


# キャラクターデータをjson形式にして返す
def get_character_data(id, uid):
    data = get_api(uid)
    json_data = create_character_data(data, id)

    return json_data
