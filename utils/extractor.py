import requests
import json
import sys
import os
#import config
from zipfile import ZipFile
class Config:
    def __init__(self):
        self.version = "1.16.5"
config = Config()

#downloads a file
def download(url, path):
    print("Downloading {url} and saving to {path}".format(url=url, path=path))
    r = requests.get(url)
    with open(path, "wb") as f:
        f.write(r.content)

#downloads the server jar for a specific version
def download_jar(version_id):
    version_manifest = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    version_manifest_dict = requests.get(version_manifest).json()

    version_dict = {}
    for version in version_manifest_dict["versions"]:
        if version["id"] == version_id:
            version_dict = requests.get(version["url"]).json()
    if version_dict == {}:
        sys.exit("no version found for version {ver}".format(ver=version_id))

    server_jar_url = version_dict["downloads"]["client"]["url"]
    jar_path = "/tmp/client.jar"
    download(server_jar_url, jar_path)
    return jar_path

#extract the full jar file
def extract_jar(jar_path="/tmp/client.jar", extracted_path=os.path.dirname(__file__)+"/minecraft/"):
    if not os.path.exists(extracted_path):
        os.mkdir(extracted_path)
    if not os.path.exists(jar_path):
        download_jar(config.version)
    with ZipFile(jar_path, "r") as zip_file:
        filenames = zip_file.namelist()
        for filename in filenames:
            zip_file.extract(filename, extracted_path)
    return extracted_path

#extracts en_us.json from a server jar
def extract_lang_file(extracted_path=os.path.dirname(__file__)+"/minecraft"):
    if not os.path.exists(extracted_path):
        extract_jar()
    lang_path = os.path.dirname(__file__)+"/en_us.json"
    os.rename(extracted_path+"/assets/minecraft/lang/en_us.json", lang_path)
    return lang_path

#gets a list of death messages from en_us.json
def generate_death_messages(lang_path):
    if not os.path.exists(lang_path):
        extract_lang_file()
    f = open(lang_path, "r")
    lang_data = json.load(f)

    death_messages = []
    for key in lang_data:
        if key == "death.attack.badRespawnPoint.message":
            message = lang_data[key].replace("%2$s", "[Intentional Game Design]")
            death_messages.append(message)
        elif key == "death.attack.badRespawnPoint.link":
            continue    
        elif key.startswith("death."):
            death_messages.append(lang_data[key])

    death_messages_path = os.path.dirname(lang_path)+"/deathmessages.json"
    data = {
        "death_messages": death_messages
    }
    with open(death_messages_path, "w") as f2:
        json.dump(data, f2)
            
    return death_messages

#gets a list of death messages (but without any arguments)
def get_death_messages():
    death_messages_path = os.path.dirname(__file__)+"/deathmessages.json"
    if not os.path.exists(death_messages_path):
        lang_path = os.path.dirname(__file__)+"/en_us.json"
        return generate_death_messages(lang_path)

    f = open(death_messages_path, "r")
    death_messages = json.load(f)["death_messages"]
    return death_messages

if __name__ == "__main__":
    #print(get_death_messages())
    extract_jar()
    
