from configparser import ConfigParser
import os
import re
from textwrap import dedent

from .Market import funcMarket
from .Wiki import funcWiki
from .Shelves import funcShelves
from .Exceptions import NoItemError, NoTownError
from .Log import logger
from .Error import errorWrite

# configの読み込み
if os.path.isfile("config.ini"):
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
else:
    # ハッシュタグ定義
    tagStr = os.environ.get("hashtagStr")
    
    # コマンド定義
    comMarket = os.environ.get("market")
    comVersion = os.environ.get("version")
    comHelp = os.environ.get("help")
    comWiki = os.environ.get("wiki")
    comShelves = os.environ.get("shelves")

# バージョン定義
DEFVER = "0.2"

# 実行部
def client(text):
    # コマンド文字列パース
    command = text.replace(f"#{tagStr}", "").replace("\n","").split()
    
    # 市場情報コマンド
    if command[0] == comMarket:
        # 商品名が1つの場合
        if len(command) == 1:
            command.extend(["-n", "none", "--end"])
        else:
            if command[-1] != "--end":
                command.append("--end") # 終端引数を追加する
            # 商品名が1つになっていない場合引数かどうかを確認する
            if len(command) >= 3 and not re.match(r"^(-[a-zA-Z]|--[a-zA-Z]+)$", command[2]): # 引数の形になっていない場合
                return "エラー: 同時に複数の商品を指定することはできません。"
            else: # 引数の形だった場合
                # 引数が正しいか判定する(変な引数は全部ここで弾かれる)
                for arg in command:
                    # 引数の形をしているが予約されていないものがあったらエラー
                    if re.match(r"^(-[a-zA-Z]|--[a-zA-Z]+)$", arg):
                        if arg not in ("-r", "-t", "--end"): # ここに最初の引数になる可能性のあるものを追加していく
                            logger(f"引数{arg}は予約されていません", "info")
                            return "エラー: 無効な引数です: " + arg
                # 第1引数[-s|-r|-n]
                if command[2] != "-r":
                    command.insert(2, "-n")
                # 第2引数/第3引数[-t ***]
                if command[3] != "-t":
                    command.insert(3, "-t")
                    command.insert(4, "none")
                else: # [-t]のときの処理
                    # 街の名前を参照したとき引数の形が出てきたら街が指定されていない
                    if re.match(r"^(-[a-zA-Z]|--[a-zA-Z]+)$", command[4]):
                        return "エラー: 引数-tに対して街の名前が指定されていません。"
                    else:
                        # 第4引数を参照して引数の形でなければ街を参照したと見做す
                        if not re.match(r"^(-[a-zA-Z]|--[a-zA-Z]+)$", command[5]):
                            return "エラー: 引数-tに対して街を複数指定することはできません。"
                
                try:
                    parseRes = funcMarket(command[1], command[2], command[4])
                    if parseRes != False:
                        res = parseRes
                    else:
                        res = f"「{command[1]}」は見つかりませんでした。"
                except NoTownError:
                    res = f"エラー: 「{command[4]}」という街は見つかりませんでした。"
                except:
                    errorWrite()
                    res = "不明なエラーが発生しました。管理者にお問い合わせください。"
                finally:
                    return res

    # Wikiコマンド
    elif command[0] == comWiki:
        try:
            res = funcWiki(command[1])
        except NoItemError:
            res = f"「{command[1]}」というアイテムは見つかりませんでした。"
        finally:
            return res

    # 棚コマンド
    elif command[0] == comShelves:
        if len(command) == 1:
            command.append("--all")
            print(command)
        try:
            res = funcShelves(command[1])
        except NoTownError:
            res = f"「{command[1]}」という街は見つかりませんでした。"
        finally:
            print(res)
            return res

    # バージョンコマンド
    elif command[0] == comVersion:
        resStr = f"SOLD OUT 2 市場情報bot for Twitter\nバージョン: {DEFVER}\n開発者: キューマン・エノビクト"
        return resStr

    # ヘルプコマンド
    elif command[0] == comHelp:
        resStr = f"以下のコマンドが使用可能です:\n{comMarket}\n{comVersion}\n{comHelp}\n{comWiki}\n{comShelves}\n\n各コマンドの詳細は以下のURLを参照してください。"
        return resStr

    # 全てに該当しない場合
    else:
        if re.match(r"[^a-zA-Z]*", command[0]): # 半角ラテンアルファベットが含まれていない場合
            return "" # 無視するようにする(コマンドを打つ気がないと判断)
        else:
            return f"Error: {command[0]}というコマンドは存在しません。"
