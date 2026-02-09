import requests
import hashlib
import os

while True:
    
    os.system('cls')

    # Ввод URl
    url = input('Вести URL мода:')

    # Выдёргиваю из url название файла + корекция от спец символов
    file_name = url.split('/')
    file_name = file_name[-1]
    index = file_name.find('%')
    while index!=-1:
        file_name = list(file_name)
        file_name[index] = '+'
        file_name = ''.join(file_name)
        index = file_name.find('%')

    # Имя мода
    mod_name = file_name[0:file_name.find('-')]
    print('Имя Файла:',file_name)

    # Установка на какой стороне работает мод
    cide_name = ['client','server','both']
    cide = cide_name[int(input('Мод работает на: 0 Клиеньте, 1 Сервере, 2 Оба\nВведите значение:'))]

    # Скачивание файла
    file = requests.get(url)
    with open(file_name, 'wb') as f:
        f.write(file.content)

    # Получение ХЕШ
    hash_func = hashlib.new('sha1')
    with open(file_name, 'rb') as f:
        hash_func.update(f.read())
        hash = hash_func.hexdigest()
        print('ХЕШ:',hash)

    os.remove(file_name)

    pw_file = open('mods/' + mod_name + '.pw.toml', 'w')
    pw_file.write(f'name = "{mod_name}"\nfilename = "{file_name}"\nside = "{cide}"\n\n[download]\nurl = "{url}"\nhash-format = "sha1"\nhash = "{hash}"\n')
    pw_file.close