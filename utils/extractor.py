import requests
import json
import sys
import os
from zipfile import ZipFile
import tempfile

class Extractor():
    def __init__(self, version, quiet=True):
        self.version = version
        self.quiet = quiet
        self.jar_path = tempfile.gettempdir() + "/client.jar"
        
    #downloads a file
    def download(self, url, path):
        if not self.quiet:
            print("Downloading {url} and saving to {path}".format(url=url, path=path))
        r = requests.get(url)
        with open(path, "wb") as f:
            f.write(r.content)

    #downloads the server jar for a specific version
    def download_jar(self, version_id):
        version_manifest = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        version_manifest_dict = requests.get(version_manifest).json()

        version_dict = {}
        for version in version_manifest_dict["versions"]:
            if version["id"] == version_id:
                version_dict = requests.get(version["url"]).json()
        if version_dict == {}:
            sys.exit("no version found for version {ver}".format(ver=version_id))

        server_jar_url = version_dict["downloads"]["client"]["url"]
        self.download(server_jar_url, self.jar_path)
        return  self.jar_path

    #extract the full jar file
    def extract_jar(self, jar_path=None, extracted_path=os.path.dirname(__file__)+"/minecraft/"):
        if jar_path == None:
            jar_path = self.jar_path
        if not os.path.exists(extracted_path):
            os.mkdir(extracted_path)
        else:
            return extracted_path
        if not os.path.exists(jar_path):
            self.download_jar(self.version)
        with ZipFile(jar_path, "r") as zip_file:
            filenames = zip_file.namelist()
            for filename in filenames:
                zip_file.extract(filename, extracted_path)
        return extracted_path

    #extracts en_us.json from a server jar
    def extract_lang_file(self, extracted_path=os.path.dirname(__file__)+"/minecraft"):
        if not os.path.exists(extracted_path):
            self.extract_jar()
        lang_path = os.path.dirname(__file__)+"/en_us.json"
        os.rename(extracted_path+"/assets/minecraft/lang/en_us.json", lang_path)
        return lang_path

    #gets a list of death messages from en_us.json
    def generate_death_messages(self, lang_path):
        if not os.path.exists(lang_path):
            self.extract_lang_file()
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
    def get_death_messages(self):
        death_messages_path = os.path.dirname(__file__)+"/deathmessages.json"
        if not os.path.exists(death_messages_path):
            lang_path = os.path.dirname(__file__)+"/en_us.json"
            return self.generate_death_messages(lang_path)

        f = open(death_messages_path, "r")
        death_messages = json.load(f)["death_messages"]
        return death_messages    
