from .getApi import getApi
from .Exceptions import NoShopError

def funcShopFromName(shopName):
    pass

def funcShopFromID(shopID):
    allshop = getApi("allshop", "https://so2-api.mutoys.com/json/shop/all.json")
    town = getApi("town", "https://so2-api.mutoys.com/master/area.json")

    # ID→店データ変換
    dl = []
    for shop in allshop:
        if shop["user_id"] == shopID:
            shopName = shop["shop_name"]
            areaID = shop["area_id"]
            posX, posY = shop["pos_x"], shop["pos_y"]
            foundationDays = shop["foundation_days"]
            honor = shop["title"]
            dl = [shopName, areaID, [posX, posY], foundationDays, honor]
            break
    if dl == []:
        raise NoShopError("such shop does not exists")
    
    # エリアID→地域名変換
    areaID_temp = dl[1]
    for col in town:
        if town[col]["area_id"] == areaID_temp:
            dl[1] = town[col]["name"]
            break
    
    return f"店名: {dl[0]}\n所在地: {dl[1]}({dl[2][0]}, {dl[2][1]})\n創業: {dl[3]}日\n称号: {dl[4]}"
