from tkinter import *
from tkinter import ttk
import requests
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
    pw_file = open('mods/' +mod_name + '.pw.toml', mode='w')
    pw_file.write(f'name = "{mod_name}"\nfilename = "{versionEntry.get("filename")}"\nside = "{side}"\n\n[download]\nurl = "{versionEntry.get("url")}"\nhash-format = "sha1"\nhash = "{hash}"\n')
    pw_file.close

window = Tk()
window.title("Packwiz utilities")

urlField = ttk.Frame()
ttk.Label(urlField, text="URL мода",padding=10).pack(side="left")
urlEntry = ttk.Entry(urlField)
urlEntry.pack(side="left")
urlField.pack()

def onButtonPress():
    work(urlEntry.get())
    urlEntry.delete(0,END)

ttk.Button(text="Обработать",command=onButtonPress).pack()

window.mainloop()