from configparser import ConfigParser
import os
import re
from textwrap import dedent

from .Market import funcMarket
from .Wiki import funcWiki
from .Shelves import funcShelves
from .Exceptions import NoItemError, NoTownError, NoShopError
from .Log import logger
from .Error import errorWrite
from .Density import funcDensity
from .Shop import funcShopFromID, funcShopFromName

if os.path.isfile("config.ini"):
    config = ConfigParser()
    config.read("config.ini")

    tagStr = config["misc"]["hashtagStr"]
    accStr = config["misc"]["accountStr"]

    comMarket = config["command"]["market"]
    comVersion = config["command"]["version"]
    comHelp = config["command"]["help"]
    comWiki = config["command"]["wiki"]
    comShelves = config["command"]["shelves"]
    comDensity = config["command"]["density"]
    comShop = config["command"]["shop"]
else:
    tagStr = os.environ.get("hashtagStr")
    accStr = os.environ.get("accountStr")

    comMarket = os.environ.get("market")
    comVersion = os.environ.get("version")
    comHelp = os.environ.get("help")
    comWiki = os.environ.get("wiki")
    comShelves = os.environ.get("shelves")
    comDensity = os.environ.get("density")
    comShop = os.environ.get("shop")

DEFVER = "0.6α"

def client(text):
    # コマンド文字列パース
    command = text.replace(f"#{tagStr}", "").replace("\n", "").split()

    # 市場情報コマンド
    if command[0] == comMarket:
        if len(command) == 1:
            return funcHelp(command[0])
        elif len(command) == 2: # 商品名が1つの場合
            command.extend(["-n", "-n", "none", "--end"])
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
                    # 街の名前を参照したとき引数の形が出てきたら、次の引数を打っているので街が指定されていない
                    if re.match(r"^(-[a-zA-Z]|--[a-zA-Z]+)$", command[4]):
                        return "エラー: 引数-tに対して街の名前が指定されていません。"
                    else:
                        # 第4引数を参照して引数の形でなければ街を参照したと見做す
                        if not re.match(r"^(-[a-zA-Z]|--[a-zA-Z]+)$", command[5]):
                            return "エラー: 引数-tに対して街を複数指定することはできません。"

        try:
            parseRes = funcMarket(command[1], command[2], command[4])
            if parseRes:
                res = parseRes
            else:
                res = f"エラー: 「{command[1]}」は見つかりませんでした。"
        except NoTownError:
            res = f"エラー: 「{command[4]}」という街は見つかりませんでした。"
        except:
            errorWrite()
            res = "不明なエラーが発生しました。管理者キューマン・エノビクトに問い合わせてください。"
        finally:
            return res

    # Wikiコマンド
    elif command[0] == comWiki:
        if len(command) == 1:
            return funcHelp(command[0])
        try:
            res = funcWiki(command[1])
        except NoItemError:
            res = f"エラー: 「{command[1]}」というアイテムは見つかりませんでした。"
        except:
            errorWrite()
            res = "不明なエラーが発生しました。管理者キューマン・エノビクトに問い合わせてください。"
        finally:
            return res

    # 棚コマンド
    elif command[0] == comShelves:
        if len(command) == 1:
            command.append("--all")
        try:
            res = funcShelves(command[1])
        except NoTownError:
            res = f"エラー: 「{command[1]}」という街は見つかりませんでした。"
        except:
            errorWrite()
            res = "不明なエラーが発生しました。管理者キューマン・エノビクトに問い合わせてください。"
        finally:
            return res

    # バージョンコマンド
    elif command[0] == comVersion:
        resStr = f"SOLD OUT 2 市場情報bot for Twitter\nバージョン: {DEFVER}\n開発者/管理者: キューマン・エノビクト"
        return resStr

    # ヘルプコマンド
    elif command[0] == comHelp:
        resStr = f"以下のコマンドが使用可能です:\n{comMarket}\n{comVersion}\n{comHelp}\n{comWiki}\n{comShelves}\n{comDensity}\n{comShop}\n\n各コマンドの詳細は以下のURLを参照してください。\nhttps://qmainconts.dev/document/so2bot.html"
        return resStr

    # 人口密度コマンド
    elif command[0] == comDensity:
        if len(command) == 1:
            return funcHelp(command[0])
        elif len(command) == 2:
            command.append("-n")
        elif len(command) == 3:
            if command[2] != "-p":
                return f"エラー: '{command[2]}'は不正な引数です。"

        try:
            res = funcDensity(command[1], command[2])
        except NoTownError:
            res = f"エラー: 「{command[1]}」という街は見つかりませんでした。"
        except:
            errorWrite()
            res = "不明なエラーが発生しました。管理者キューマン・エノビクトに問い合わせてください。"
        finally:
            return res

    # 店舗情報コマンド
    elif command[0] == comShop:
        if len(command) == 1:
            return funcHelp(command[0])
        elif len(command) != 3:
            return "エラー: コマンドの形式が不正です。"
        else:
            if re.match(r"^(-[a-zA-Z]|--[a-zA-Z]+)$", command[1]): # 引数の形判定
                if command[1] not in ("-i", "-n"):# ここに最初の引数になる可能性のあるものを追加していく
                    res = f"エラー: '{command[1]}'は不正な引数です。"
                else:
                    if command[1] == "-i":
                        if command[2].startswith("#"):
                            command[2] = command[2][1:]
                        try:
                            ownerID = int(command[2])
                            try:
                                res = funcShopFromID(ownerID)
                            except NoShopError:
                                res = f"エラー: オーナー番号'{ownerID}'の店舗は見つかりませんでした。"
                        except ValueError:
                            res = "エラー: IDは半角数字で入力してください。"
                    elif command[1] == "-n":
                        shopName = command[2]
                        try:
                            res = funcShopFromName(shopName)
                        except NoShopError:
                            res = f"エラー: '{shopName}'という名前の店舗は見つかりませんでした。"
            else:
                res = "エラー: コマンドの形式が不正です。"
            return res

    # 全てに該当しない場合
    else:
        if re.match(r"[^a-zA-Z]", command[0]): # 半角ラテンアルファベットが含まれていない場合
            return "" # 無視するようにする(コマンドを打つ気がないと判断)
        else:
            return f"エラー: {command[0]}というコマンドは存在しません。"

# ヘルプ用関数
def funcHelp(command):
    # 市場情報コマンド
    if command == comMarket:
        return "使用方法: market [商品名] [-r] [-t 街名]\n詳細は以下のドキュメントをご確認ください。\nhttps://qmainconts.dev/document/so2bot.html"
    # Wikiコマンド
    elif command == comWiki:
        return "使用方法: wiki [商品名]\n詳細は以下のドキュメントをご確認ください。\nhttps://qmainconts.dev/document/so2bot.html"
    # 人口密度コマンド
    elif command == comDensity:
        return "使用方法: density [街名] [-p]\n詳細は以下のドキュメントをご確認ください。\nhttps://qmainconts.dev/document/so2bot.html"
    # 店舗情報コマンド
    elif command == comShop:
        return "使用方法: shop [-i|-n] [オーナー番号もしくは名前]\n詳細は以下のドキュメントをご確認ください。\nhttps://qmainconts.dev/document/so2bot.html"
    else:
        return "不明なエラーが発生しました。管理者キューマン・エノビクトに問い合わせてください。"
