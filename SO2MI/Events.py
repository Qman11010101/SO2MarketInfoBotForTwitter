from configparser import ConfigParser
import datetime
import json
import os
import re
import textwrap
import traceback

from .Log import logger

import pytz
import requests
from bs4 import BeautifulSoup

if os.path.isfile("config.ini"):
    config = ConfigParser()
    config.read("config.ini")
    
    regEventDay = config["misc"]["RegEventDay"]
    tz = config["misc"]["timezone"]
else:
    regEventDay = os.environ.get("regEventDay")
    tz = os.environ.get("timezone")

def funcEvent():
    try:
        logger("イベント情報を取得します")

        # ページダウンロード
        pseudoUserAgent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"}
        source = requests.get("https://so2-bbs.mutoys.com/agenda", headers=pseudoUserAgent)
        bsobj = BeautifulSoup(source.text, "html.parser")

        # preloadデータのあるdivを拾う
        preloadDiv = bsobj.find_all(id="data-preloaded")

        # 各イベント告知ページへのリンクを取得する
        linksTag = bsobj.find_all("meta", itemprop="url")

        linkurls = []
        for tag in linksTag:
            linkurls.append(tag["content"])

        # 文字列操作
        convQuot = str(preloadDiv[0]).replace(r"\&quot;", '"').replace("&quot;", '"') # 特殊文字をダブルクォーテーションに置換
        rugueux = convQuot[convQuot.find('"topic_list_agenda":'):] # 誤動作防止のため大まかに切り取る
        topicsRug = "{" + rugueux[rugueux.find('"topics":'):rugueux.find("}}")] + "}" # JSONの形で切り取り、足りない括弧をつける
        topicsRug2 = re.sub(r'"fancy_title":.*?",', "", topicsRug)
        topicsJson = re.sub(r'"excerpt":.*?",', "", topicsRug2)
        with open("agenda.json", "w", encoding="utf-8_sig") as agw: # 一旦保存してJSONとして扱えるようにする
            agw.write(topicsJson)
        with open("agenda.json", "r", encoding="utf-8_sig") as agr: # 保存したJSONを読み込む
            agenda = json.load(agr)

        topiclist = agenda["topics"] # 必要な情報が入ったリストを生成する

        iCount = 0
        timezone = pytz.timezone(config["misc"]["timezone"])
        now = datetime.datetime.now(timezone)
        eventHeld = [] # 開催中
        eventCome = [] # 近日
        for col in topiclist:
            # タイトル取得
            title = col["title"]

            # リンク取得
            link = linkurls[iCount]

            # 開始時刻取得
            startTimeutc = datetime.datetime.strptime(col["event"]["start"], "%Y-%m-%dT%H:%M:%S%z")
            startTimejst = startTimeutc.astimezone(timezone)
            startTime = f"{startTimejst.month}/{startTimejst.day} {startTimejst.hour}:{startTimejst:%M}"

            # 終了時刻取得
            if "end" in col["event"]: # 終了時刻明記
                endTimeutc = datetime.datetime.strptime(col["event"]["end"], "%Y-%m-%dT%H:%M:%S%z")
                endTimejst = endTimeutc.astimezone(timezone)
                endTime = f"{endTimejst.month}/{endTimejst.day} {endTimejst.hour}:{endTimejst:%M}"
            else: # 終了時刻がない場合は終日開催と見做す
                endTimejst = startTimejst + datetime.timedelta(hours=24)
                endTime = f"{endTimejst.month}/{endTimejst.day} {endTimejst.hour}:{endTimejst:%M}"

            if now <= endTimejst: # 終了済みイベントは表示しない
                if now >= startTimejst: # 開催中
                    event = f"{endTime}終了"
                    eventInfo = [event, title, link]
                    eventHeld.append(eventInfo)
                elif startTimejst.timestamp() - now.timestamp() < (int(regEventDay) * 86400):
                    event = f"{startTime} ～ {endTime}"
                    eventInfo = [event, title, link]
                    eventCome.append(eventInfo)

            iCount += 1

        # イベントごとの文章構築
        eventHeldText = []
        eventComeText = []
        if len(eventHeld) != 0:
            for ev in eventHeld:
                evtxt = textwrap.dedent(f"""
                {ev[0]}: {ev[1]}
                Topic: {ev[2]}""")
                eventHeldText.append(evtxt)
        if len(eventCome) != 0:
            for ev in eventCome:
                evtxt = textwrap.dedent(f"""
                {ev[0]}: {ev[1]}
                Topic: {ev[2]}""")
                eventComeText.append(evtxt)

        eventText = eventHeldText + eventComeText
        with open("event.txt", "w", encoding="utf-8_sig") as evtxtarr:
            evtxtarr.write(str(eventText))
    except:
        traceback.print_exc()
        return False
