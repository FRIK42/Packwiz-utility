import json
import os
import zipfile
from os import write

import requests

def work(url:str):
    #Обработка URL
    _parts = url.removeprefix("https://modrinth.com/mod").split("/")
    mod_name=_parts[1]
    version_number=_parts[3]

    #Запросы к Modrinth
    projectReq:dict = requests.get("https://api.modrinth.com/v2/project/"+mod_name).json()
    if(projectReq.get("error")): raise ConnectionError("Проект не найден")
    versionReq:dict = requests.get("https://api.modrinth.com/v2/project/"+mod_name+"/version/"+version_number).json()

    #Найти основной файл версии
    def getPrimaryFile(versionJSON:dict):
        for version in versionJSON.get("files"):
            if(version.get("primary")): return version
            raise ValueError("Не найдена основная версия")
    versionEntry = getPrimaryFile(versionReq)

    #Получение хеша
    hash = versionEntry.get("hashes").get("sha1")

    #Получение стороны мода
    side = ["both","client","server","both"][(len(projectReq.get("client_side"))==8)+(len(projectReq.get("server_side"))==8)*2] # Самый читаемый код

    #Запись в файл
    pw_file = open('mods/' +mod_name + '.pw.toml', 'w')
    pw_file.write(f'name = "{mod_name}"\nfilename = "{versionEntry.get("filename")}"\nside = "{side}"\n\n[download]\nurl = "{versionEntry.get("url")}"\nhash-format = "sha1"\nhash = "{hash}"\n')
    pw_file.close

def makeTOMLFile(name:str,filename:str,side:str,download:str,sha1:str):
    open('mods/'+name+'.toml', 'w').write(
        f'name = "{name}"\n'
        f'filename = "{filename}"\n'
        f'side = "{side}"\n'
        f'\n[download]\n'
        f'url = "{download}"\n'
        f'hash-format = "sha1"'
        f'\nhash = "{sha1}"\n'
    )
    print(f"Успешно создан файл для {name}")
def getFromModrinth(filename:str):
    project = requests.get(f"https://api.modrinth.com/v2/search?query={getModID(filename)}&facets={json.dumps([["project_type:mod"],["categories:fabric"],["versions:1.20.1"]])}&limit=1").json().get("hits")[0]
    modID = project.get("slug")

    versionQuery = requests.get(f"https://api.modrinth.com/v2/project/{modID}/version?loaders=[\"fabric\"]&game_versions=[\"1.20.1\"]&include_changelog=false").json()
    for version in versionQuery:
        for modrinthFile in version.get("files"):
            if not modrinthFile.get("primary"): continue
            statedName = modrinthFile.get("filename")
            if statedName==filename.split("/")[-1]:
                makeTOMLFile(
                    modID,
                    statedName,
                    ["both","server","client"][(len(project.get("client_side"))=="unsupported")+(len(project.get("server_side"))=="unsupported")*2],
                    modrinthFile.get("url"),
                    modrinthFile.get("hashes").get("sha1")
                )
                os.remove(filename)
                return True
    else: return False

def getModID(jar_path:str):
    with zipfile.ZipFile(jar_path, 'r') as jar:
        for filename in jar.namelist():
            if filename == "fabric.mod.json":
                contents = jar.read(filename)
                try:
                    return json.loads(contents).get("id")
                except json.decoder.JSONDecodeError:
                    print(jar.filename+" уёбок такой сломан, чиним.")
                    return json.loads(contents.decode('utf-8').replace('\n', '').encode('utf-8')).get("id")
        raise ValueError("Не найден файл fabric.mod.json")

def processFile(filePath:str):
    if filePath.endswith(".jar"):
        try:
            getFromModrinth(filePath)
        except Exception: print(f"Не удалось обработать {filePath}")

def parseFolder(folder:str):
    for fileName in os.listdir(folder):
        processFile(folder+"/"+fileName)
parseFolder("mods")

exit()
with open('modrinth.txt') as f:
    for e in f:
        work(e.replace('\n',''))