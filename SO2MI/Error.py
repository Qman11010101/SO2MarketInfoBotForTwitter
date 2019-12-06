import datetime
import os
from configparser import ConfigParser
import traceback

from pytz import timezone

if os.path.isfile("config.ini"):
    config = ConfigParser()
    config.read("config.ini")
    tz = config["misc"]["timezone"]
else:
    tz = os.environ.get("timezone")

def errorWrite():
    now = datetime.datetime.now(timezone(tz))
    nowFormat = now.strftime("%Y/%m/%d %H:%M:%S%z")
    nowFileFormat = now.strftime("%Y%m%d")
    os.makedirs("error-log", exist_ok=True)
    with open(f"error-log/{nowFileFormat}.txt", "a") as f:
        f.write(f"--- Datetime: {nowFormat} ---\n")
        traceback.print_exc(file=f)
        f.write("\n")
    traceback.print_exc()