from configparser import ConfigParser
import re

from .Market import funcMarket
from .Wiki import funcWiki
from .Shelves import funcShelves

# config読み込み
config = ConfigParser()
config.read("config.ini")

# ハッシュタグ定義
tagStr = config["misc"]["hashtagStr"]

# コマンド定義
comMarket = config["command"]["market"]
comVersion = config["command"]["version"]
comHelp = config["command"]["help"]
comWiki = config["command"]["wiki"]
comShelves = config["command"]["shelves"]

# バージョン定義
DEFVER = "0.1"

# 実行部
def client(text): # TODO: 市場情報関数に渡すコマンドをパースする処理を書く、返ってきた値をそのままreturnするようにする。helpとversionは直書き
    # コマンド文字列パース
    command = text.replace(f"#{tagStr}", "").replace("\n","").split()
    
    # 市場情報コマンド
    if command[0] == comMarket:
        pass

    # Wikiコマンド
    elif command[0] == comWiki:
        pass

    # 棚コマンド
    elif command[0] == comShelves:
        pass

    # バージョンコマンド
    elif command[0] == comVersion:
        resStr = f"SOLD OUT 2 市場情報bot for Twitter\nバージョン: {DEFVER}\n開発者: キューマン・エノビクト"
        return resStr

    # ヘルプコマンド
    elif command[0] == comHelp:
        pass

    # 全てに該当しない場合
    else:
        if re.match(r"[^a-zA-Z]*", command[0]): # 半角ラテンアルファベットが含まれていない場合
            return "" # 無視するようにする(コマンドを打つ気がないと判断)
        else:
            return f"Error: {command[0]}というコマンドは存在しません。"
