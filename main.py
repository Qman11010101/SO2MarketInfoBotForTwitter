#!/usr/bin/env python3

# SOLD OUT 2 Market Infomation Bot for Twitter
# Author: Kjuman Enobikto
# License: MIT License

from configparser import ConfigParser
import json
import os
import sys
import threading
import time

from requests_oauthlib import OAuth1Session

from SO2MI.Client import client
from SO2MI.Log import logger

# configの読み込み
if os.path.isfile("config.ini"):
    config = ConfigParser()
    config.read("config.ini")

    # APIキー定義
    consumerKey = config["keys"]["consumerKey"]
    consumerSecret = config["keys"]["consumerSecret"]
    accessToken = config["keys"]["accessToken"]
    accessTokenSecret = config["keys"]["accessTokenSecret"]

    # ハッシュタグ定義
    tagStr = config["misc"]["hashtagStr"]

# 環境変数の読み込み
else:
    # APIキー定義
    consumerKey = os.environ.get("consumerKey")
    consumerSecret = os.environ.get("consumerSecret")
    accessToken = os.environ.get("accessToken")
    accessTokenSecret = os.environ.get("accessTokenSecret")

    # ハッシュタグ定義
    tagStr = os.environ.get("hashtagStr")

stream = "https://stream.twitter.com/1.1/statuses/filter.json"
tweet = "https://api.twitter.com/1.1/statuses/update.json"

if __name__ == "__main__":
    # 定期実行関数定義
    def regexc():
        # 取得してツイートするもの(ツイートは1度に5つまでを目安)
        # ・イベント情報
        # ・ランキング上位数人
        # ・月末月始の優待券使用奨励
        # 定期ツイートは8時/12時/16時/20時
        pass

    # メイン関数定義
    def mainfunc():
        session = OAuth1Session(consumerKey, consumerSecret, accessToken, accessTokenSecret)
        tracker = {"track":f"#{tagStr}"}
        while True:
            resGet = session.post(stream, params=tracker, stream=True)
            for line in resGet.iter_lines():
                logger(line.decode("utf-8"), "debug") # デバッグ用
                if line.decode("utf-8") == "Exceeded connection limit for user":
                    logger("制限中です")
                    time.sleep(1000) # 17分弱ストップ
                    continue
                if line.decode("utf-8") != "":
                    content = json.loads(line.decode("utf-8"))
                    command = content["text"]
                    tweetId = content["id"]
                    if "RT" not in command:
                        reply = client(command)
                        if reply != "":
                            mention = {"status":reply, "in_reply_to_status_id":tweetId, "auto_populate_reply_metadata":True}
                            resPost = session.post(tweet, params=mention)
                            try:
                                logger(resPost["errors"][0]["message"], "error")
                            except:
                                pass

    # 定期実行スレッドのデーモン化
    th = threading.Thread(target=regexc, name="th", args=())
    th.setDaemon(True)

    # 実行
    mainfunc()
    th.start()
