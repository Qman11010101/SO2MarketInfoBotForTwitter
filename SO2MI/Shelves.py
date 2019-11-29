def funcShelves(townName):
    import textwrap
    import datetime
    import glob
    from collections import Counter

    from .getApi import getApi
    from .Exceptions import NoTownError

    # API取得部
    town = getApi("town", "https://so2-api.mutoys.com/master/area.json")
    sale = getApi("sale", "https://so2-api.mutoys.com/json/sale/all.json")
    item = getApi("item", "https://so2-api.mutoys.com/master/item.json")
    recipe = getApi("recipe", "https://so2-api.mutoys.com/json/master/recipe_item.json")

    # 街ID取得部
    if townName != "--all":
        townId = 0
        for col in town:
            if town[col]["name"] == townName:
                townId = int(town[col]["area_id"])
                break
        if int(townId) == 0:
            raise NoTownError("such town does not exists")

    # 変数初期化部
    sumShelf = sumShelfBundle = sumShelfNotBundle = 0
    sumPrice = sumPriceBundle = sumPriceNotBundle = 0
    shelfBundlePercent = shelfNotBundlePersent = 0
    priceBundlePercent = priceNotBundlePercent = 0
    itemsIDList = []

    # 棚数・販売額・アイテムID取得部
    if townName != "--all":
        for col in range(len(sale)):
            if sale[col]["area_id"] == townId:
                sumShelf += 1
                sumPrice += int(sale[col]["price"] * sale[col]["unit"])
                itemUnitList = [sale[col]["item_id"]] * sale[col]["unit"]
                itemsIDList.extend(itemUnitList)
                if sale[col]["bundle_sale"]:
                    sumShelfBundle += 1
                    sumPriceBundle += int(sale[col]["price"] * sale[col]["unit"])
    else:
        for col in range(len(sale)):
            sumShelf += 1
            sumPrice += int(sale[col]["price"] * sale[col]["unit"])
            itemUnitList = [sale[col]["item_id"]] * sale[col]["unit"]
            itemsIDList.extend(itemUnitList)
            if sale[col]["bundle_sale"]:
                sumShelfBundle += 1
                sumPriceBundle += int(sale[col]["price"] * sale[col]["unit"])

    # 非まとめ売り算出
    sumShelfNotBundle = sumShelf - sumShelfBundle
    sumPriceNotBundle = sumPrice - sumPriceBundle

    # まとめ売り百分率
    shelfBundlePercent = float("{:.2f}".format((sumShelfBundle / sumShelf) * 100))
    priceBundlePercent = float("{:.2f}".format((sumPriceBundle / sumPrice) * 100))

    # 非まとめ売り百分率
    shelfNotBundlePersent = 100 - shelfBundlePercent
    priceNotBundlePercent = 100 - priceBundlePercent

    # 全体のときの文字の入れかえ("--all"→"全体")
    if townName == "--all":
        townName = "全体"

    # 時刻をsale-*.jsonから推測
    target = glob.glob("api-log/sale-*.json")
    jsonTime = datetime.datetime.strptime(target[0].replace("\\", "/"), "api-log/sale-%y%m%d%H%M.json")

    retStr = textwrap.dedent(f"""
    {jsonTime.strftime("%H{0}%M{1}").format("時", "分")}現在の{townName}の合計販売額・販売棚数は以下の通りです。

    合計販売額: {str("{:,}".format(sumPrice))}G
    　まとめ売り: {str("{:,}".format(sumPriceBundle))}G ({priceBundlePercent}%)
    　ばら売り: {str("{:,}".format(sumPriceNotBundle))}G ({priceNotBundlePercent}%)

    販売棚数: {str("{:,}".format(sumShelf))}個
    　まとめ売り: {str("{:,}".format(sumShelfBundle))}個 ({shelfBundlePercent}%)
    　ばら売り: {str("{:,}".format(sumShelfNotBundle))}個 ({shelfNotBundlePersent}%)
    """)

    return retStr
