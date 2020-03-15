import datetime
import glob
import textwrap

from .getApi import getApi
from .Exceptions import NoTownError

def funcDensity(townName, argument=""):
    if argument == "-p":
        shopcount = getApi("shopsummary", "https://so2-api.mutoys.com/json/shop/summary.json")
    else:
        population = getApi("population", "https://so2-api.mutoys.com/json/people/all.json")
    town = getApi("town", "https://so2-api.mutoys.com/master/area.json")

    # 街ID取得
    townId = 0
    for col in town:
        if town[col]["name"] == townName:
            townId = int(town[col]["area_id"])
            break
    if int(townId) == 0:
        raise NoTownError("such town does not exists")

    townArea = town[str(townId)]["width"] * town[str(townId)]["height"]
    if argument == "-p":
        for col in range(len(shopcount)):
            if shopcount[col]["area_id"] == townId:
                townShopCount = shopcount[col]["count"]
                break
        townDensity = townShopCount / townArea
    else:
        for col in range(len(population)):
            if population[col]["area_id"] == townId:
                townPopulation = population[col]["unit"]
                break
        townDensity = townPopulation / townArea

    # 時刻をtown-*.jsonから推測
    target = glob.glob("api-log/town-*.json")
    jsonTime = datetime.datetime.strptime(
        target[0].replace("\\", "/"), "api-log/town-%y%m%d%H%M.json")

    if argument == "-p":
        resStr = textwrap.dedent(f"""
        {jsonTime.strftime("%H{0}%M{1}").format("時", "分")}現在の{townName}の情報は以下の通りです。

        店数: {townShopCount}店
        面積: {townArea}マス
        人口密度: {"{:.3g}".format(townDensity)}人/マス
        """)
    else:
        resStr = textwrap.dedent(f"""
        {jsonTime.strftime("%H{0}%M{1}").format("時", "分")}現在の{townName}の情報は以下の通りです。

        人口: {townPopulation}人
        面積: {townArea}マス
        人口密度: {"{:.3g}".format(townDensity)}人/マス
        """)

    return resStr
