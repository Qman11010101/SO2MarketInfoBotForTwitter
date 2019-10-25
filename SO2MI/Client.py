from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

tagStr = config["misc"]["hashtagStr"]

def testo(command):
    parsed = command.replace(f"#{tagStr}", "")
    return parsed + "あ"
