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
    accStr = config["misc"]["accountStr"]

else:
    consumerKey = os.environ.get("consumerKey")
    consumerSecret = os.environ.get("consumerSecret")
    accessToken = os.environ.get("accessToken")
    accessTokenSecret = os.environ.get("accessTokenSecret")

    tagStr = os.environ.get("hashtagStr")
    accStr = os.environ.get("accountStr")

stream = "https://stream.twitter.com/1.1/statuses/filter.json"
tweet = "https://api.twitter.com/1.1/statuses/update.json"

if __name__ == "__main__":

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

    # セッション生成
    session = OAuth1Session(consumerKey, consumerSecret, accessToken, accessTokenSecret)

    # 実行
    mainfunc()
