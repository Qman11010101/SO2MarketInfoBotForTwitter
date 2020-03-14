import datetime
import glob
import textwrap

from .getApi import getApi
from .Exceptions import NoTownError

def funcDensity(townName):
    population = getApi("population", "https://so2-api.mutoys.com/json/people/all.json")
    town = getApi("town", "https://so2-api.mutoys.com/master/area.json")

    # 街ID取得
    if townName != "--all":
        townId = 0
        for col in town:
            if town[col]["name"] == townName:
                townId = int(town[col]["area_id"])
                break
        if int(townId) == 0:
            raise NoTownError("such town does not exists")
    else:
        return "引数--allにはまだ対応していません。ご了承ください。"

    for col in range(len(population)):
        if population[col]["area_id"] == townId:
            townPopulation = population[col]["unit"]
            break
    townArea = town[str(townId)]["pos_x"] * town[str(townId)]["pos_y"]
    townDensity = townPopulation / townArea

    # 時刻をtown-*.jsonから推測
    target = glob.glob("api-log/town-*.json")
    jsonTime = datetime.datetime.strptime(
        target[0].replace("\\", "/"), "api-log/town-%y%m%d%H%M.json")

    retStr = textwrap.dedent(f"""
    {jsonTime.strftime("%H{0}%M{1}").format("時", "分")}現在の{townName}の情報は以下の通りです。

    人口: {townPopulation}人
    面積: {townArea}マス
    人口密度: {"{:.3g}".format(townDensity)}人/マス
    """)

    return retStr
