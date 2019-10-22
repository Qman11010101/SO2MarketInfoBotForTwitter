#!/usr/bin/env python3

# SOLD OUT 2 Market Infomation Bot for Twitter
# Author: Kjuman Enobikto
# License: MIT License

from configparser import ConfigParser
import json
import os, sys

from requests_oauthlib import OAuth1Session

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

stream = "https://stream.twitter.com/1.1/statuses/filter.json"
tweet = "https://api.twitter.com/1.1/statuses/update.json"

if __name__ == "__main__":
    session = OAuth1Session(consumerKey, consumerSecret, accessToken, accessTokenSecret)
    tracker = {"track":"#これはテスト用ですよ"}
    resGet = session.post(stream, params=tracker, stream=True)
    for line in resGet.iter_lines():
        print(line.decode("utf-8"))
        content = json.loads(line.decode("utf-8"))
        userName = content["user"]["name"]
        text = content["text"]
        screenName = content["user"]["screen_name"]
        tweetId = content["id"]
        print(userName + " said: " + text)
        reply = "テストは成功です"
        mention = {"status":reply, "in_reply_to_status_id":tweetId}
        resPost = session.post(tweet, params=mention)        
