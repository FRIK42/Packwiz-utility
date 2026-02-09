import json
import os
import zipfile
import hashlib
import requests

def makeTOMLFile(name:str,filename:str,side:str,download:str,sha1:str):
    open('mods/'+name+'.pw.toml', 'w').write(
        f'name = "{name}"\n'
        f'filename = "{filename}"\n'
        f'side = "{side}"\n'
        f'\n[download]\n'
        f'url = "{download}"\n'
        f'hash-format = "sha1"'
        f'\nhash = "{sha1}"\n'
    )

def getFromModrinth(project:dict,filename:str,replace:bool=True)->bool:
    filehash = hashlib.sha1(open(filename,"rb").read(),usedforsecurity=False).hexdigest()
    modID = project.get("slug")
    print(f"Получение {filename.split('/')[-1]} с Modrinth как {modID}...",end=' ')
    versionQuery = requests.get(f"https://api.modrinth.com/v2/project/{modID}/version",{
        "loaders":json.dumps(["fabric"]),
        "game_versions":json.dumps(["1.20.1"]),
        "include_changelog":"false"
    }).json()
    for version in versionQuery:
        for modrinthFile in version.get("files"):
            if not modrinthFile.get("primary"): continue #Пропуск побочных файлов
            if filehash==modrinthFile.get("hashes").get("sha1"): #Если точно такой же файл существует на Modrint
                makeTOMLFile(
                    modID,
                    modrinthFile.get("filename"),
                    ["both","server","client"][(len(project.get("client_side"))==11)|(len(project.get("server_side"))==11)<<1], #Чистый код
                    modrinthFile.get("url"),
                    filehash
                )
                if replace: os.remove(filename)
                print("Успешно")
                return True
    else:
        print("Файл не найден")
        return False


def getFabricModJSON(jar:str)->dict:
    return json.loads(
        zipfile.ZipFile(jar)
        .read("fabric.mod.json")
        .decode('utf-8')
        .replace('\n', '')
        .encode('utf-8')
    )

def searchProj(query: str) -> dict | None:
    if len(projects := requests.get("https://api.modrinth.com/v2/search", params={
        "query": query,
        "facets": json.dumps([
            ["project_type:mod"], ["categories:fabric"], ["versions:1.20.1"]
        ]),
        "limit": 1,
    }).json().get("hits"))!=0: return projects[0]
    else: return None

def parseFolder(folder:str):
    jars = dict() #Хранить путь до файла мода и его fabric.mod.json под его id, id:[путь,fabric.mod.json]
    print("Индексирование файлов...",end='')
    for name in os.listdir(folder):
        path=folder+"/"+name
        if path.endswith(".jar"):
            fabricModJSON = getFabricModJSON(path)
            jars[fabricModJSON.get("id")]=[path,fabricModJSON]
        elif path.endswith(".disabled"): os.remove(path)
    print("Готово")

    print("\n=====Запросы по ID мода=====")
    for project in requests.get(f"https://api.modrinth.com/v2/projects?ids={json.dumps([j for j in jars.keys()])}").json():
        if (modID := project.get("slug")) is not None:
            if getFromModrinth(project,jars[modID][0]): jars.pop(modID)

    print("\n=====Запросы по названию мода=====")
    for modID, pathPlusJson in jars.copy().items():
        if (project := searchProj(pathPlusJson[1].get("name"))) is not None:
            if getFromModrinth(project,pathPlusJson[0]): jars.pop(modID)

    print("\n=====Поиск по имени файла=====")
    for modID, pathPlusJson in jars.copy().items():
        if (project := searchProj(
            str(pathPlusJson[0]).split("/")[-1].removesuffix(".jar").removesuffix(pathPlusJson[1].get("version"))
        )) is not None:
            if getFromModrinth(project,pathPlusJson[0]): jars.pop(modID)


    print("\nНеобработанные моды:")
    for v in jars.values():
        print(str(v[0].split("/")[-1]))

parseFolder("mods")