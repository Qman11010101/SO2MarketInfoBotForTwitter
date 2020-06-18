#!/usr/bin/env python3

# SOLD OUT 2 Market Infomation Bot for Twitter
# Author: Kjuman Enobikto
# License: MIT License

from configparser import ConfigParser
import asyncio
import datetime
import json
import os
import sys
import threading
import time

from requests_oauthlib import OAuth1Session

from SO2MI.Client import client
from SO2MI.Log import logger
from SO2MI.Events import funcEvent

if os.path.isfile("config.ini"):
    config = ConfigParser()
    config.read("config.ini")

    consumerKey = config["keys"]["consumerKey"]
    consumerSecret = config["keys"]["consumerSecret"]
    accessToken = config["keys"]["accessToken"]
    accessTokenSecret = config["keys"]["accessTokenSecret"]

    tagStr = config["misc"]["hashtagStr"]

else:
    consumerKey = os.environ.get("consumerKey")
    consumerSecret = os.environ.get("consumerSecret")
    accessToken = os.environ.get("accessToken")
    accessTokenSecret = os.environ.get("accessTokenSecret")

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
        while True:
            logger("定期投稿システム実行中", "debug")
            time.sleep(300) # 5分ごとにチェック

            # 時間取得
            hour = datetime.datetime.now().hour
            minu = datetime.datetime.now().minute

            # 分岐
            if hour == 8 and 0 <= minu <= 5:
                logger("8時の処理を開始します", "debug")
            elif hour == 12 and 0 <= minu <= 5:
                logger("12時の処理を開始します", "debug")
            elif hour == 16 and 0 <= minu <= 5:
                logger("16時の処理を開始します", "debug")
            elif hour == 20 and 0 <= minu <= 5:
                logger("20時の処理を開始します", "debug")
                # イベント投稿(1日1回)
                res = funcEvent()
                if len(res):
                    for post in range(min(5, len(res))):
                        content = {"status": res[post]}
                        resPost = session.post(tweet, params=content)
                        asyncio.sleep(5)
            else:
                pass

    # メイン関数定義
    def mainfunc():
        tracker = {"track":f"#{tagStr}"}
        while True:
            resGet = session.post(stream, params=tracker, stream=True)
            for line in resGet.iter_lines():
                if line.decode("utf-8") == "Exceeded connection limit for user":
                    logger("制限中です")
                    time.sleep(1000)
                    continue
                if line.decode("utf-8") != "":
                    content = json.loads(line.decode("utf-8"))
                    command = content["text"]
                    tweetId = content["id"]
                    logger(f"{content['user']['name']} (@{content['user']['screen_name']}): {content['text']}")
                    if "RT" not in command:
                        reply = client(command)
                        if reply != "":
                            mention = {"status":reply, "in_reply_to_status_id":tweetId, "auto_populate_reply_metadata":True}
                            resPost = session.post(tweet, params=mention)
                            try:
                                logger(resPost["errors"][0]["message"], "error")
                            except:
                                logger("投稿完了しました")
                                pass

    # 定期実行スレッドのデーモン化
    th = threading.Thread(target=regexc, name="th", args=())
    th.setDaemon(True)

    # セッション生成
    session = OAuth1Session(consumerKey, consumerSecret, accessToken, accessTokenSecret)

    # 実行
    mainfunc()
    th.start()
