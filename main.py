#!/usr/bin/env python3

# SOLD OUT 2 Market Infomation Bot for Twitter
# Author: Kjuman Enobikto
# License: MIT License

from configparser import ConfigParser
import json
import os
import sys
import time

from requests_oauthlib import OAuth1Session
from SO2MI.Client import *

# configの読み込み
if os.path.isfile("config.ini"):
    config = ConfigParser()
    config.read("config.ini")
else:
    print("エラー: 設定ファイルがありません")
    sys.exit(1) # 異常終了

# APIキー定義
consumerKey = config["keys"]["consumerKey"]
consumerSecret = config["keys"]["consumerSecret"]
accessToken = config["keys"]["accessToken"]
accessTokenSecret = config["keys"]["accessTokenSecret"]
tagStr = config["misc"]["hashtagStr"]

stream = "https://stream.twitter.com/1.1/statuses/filter.json"
tweet = "https://api.twitter.com/1.1/statuses/update.json"

if __name__ == "__main__":
    session = OAuth1Session(consumerKey, consumerSecret, accessToken, accessTokenSecret)
    tracker = {"track":f"#{tagStr}"}
    while True:
        resGet = session.post(stream, params=tracker, stream=True)
        for line in resGet.iter_lines():
            print(line.decode("utf-8")) # デバッグ用
            if line.decode("utf-8") == "Exceeded connection limit for user": # TODO: エラーになったら停止することをツイート
                print("制限中")
                time.sleep(1000) # 17分弱ストップ
                continue
            content = json.loads(line.decode("utf-8"))
            command = content["text"]
            tweetId = content["id"]
            if "RT" not in command:
                reply = testo(command)
                mention = {"status":reply, "in_reply_to_status_id":tweetId, "auto_populate_reply_metadata":True}
                resPost = session.post(tweet, params=mention) # TODO: エラー処理/エラーになったら停止することをツイート
