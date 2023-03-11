import codecs, json


# jsonファイルの読み込み
def read_json(path):  # 引数：jsonファイルのパス
    with codecs.open(path,encoding='utf-8') as f:
        data = json.load(f)
    return data
