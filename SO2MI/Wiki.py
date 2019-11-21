import textwrap
from urllib import parse

from .getApi import getApi
from .Exceptions import NoItemError

def funcWiki(itemName):
    item = getApi("item", "https://so2-api.mutoys.com/master/item.json")

    itemId = 0
    for col in item:
        if item[str(col)]["name"] == itemName:
            itemId = col
            category = item[str(col)]["category"]
            break
    if int(itemId) == 0:
        raise NoItemError("nonexistent of item")
    
    wikiurl = f"https://wikiwiki.jp/sold2/%E3%82%A2%E3%82%A4%E3%83%86%E3%83%A0/{parse.quote(category)}/{parse.quote(itemName)}"
    msg = textwrap.dedent(f"""
    {wikiurl}

    ページは存在しない場合があります。
    """)

    return msg
