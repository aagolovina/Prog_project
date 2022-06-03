#! python -m pip install langdetect
#! python -m pip install python-Levenshtein

from langdetect import detect
import Levenshtein as lev
import re, string

lv_alphabet = re.compile(r'[A-Za-zĀāČčĒēĢģĪīĶķĻļŅņŠšŪūŽž]+')
lt_alphabet = re.compile(r'[A-Za-zĄąČčĘęĖėĮįŠšŲųŪūŽž]+')

def replace_with_correct(token, wordlist):
    dist = {}
    for word in wordlist:
        dist[word] = lev.distance(token, word) # ключ -- словоформа из корпуса, значение -- расстояние относительно неправильного токена из пользовательского файла
    optimal_dist = min(list(dist.values()))
    optimal_candidate = [i for i in dist if dist[i] == optimal_dist]
    return optimal_candidate[0] # дубовая замена на первый элемент в списке словоформ с наименьшим расстоянием

def indicate_wrong(token, marker):
    indication = {
        'полужирный':'__',
        'курсив':'_'
    }
    res = f'{indication[marker]}{token}{indication[marker]}'
    return res

print("""Добро пожаловать в наше проектное приложение!\n\nНаш спеллчекер позволяет проверить правописание текстов на литовском и латышском языке. Приложение предлагает не только замену слов с опечатками, но и выделение их полужирным или курсивным шрифтом. Вам необходимо только загрузить файл с текстом и выбрать режим обработки. Принимаются только файлы с расширением .txt в кодировке UTF-8. Если ваш файл не соответствует этим требованиям, пожалуйста, конвертируйте его перед загрузкой.""")

file_upload = input('Введите название файла: ')

langcode = {
    'lv':'Latvian',
    'lt':'Lithuanian'
}

with open(file_upload, 'r', encoding = 'utf-8') as f:
    text = f.read() # это текст пользователя
    code = detect(text)
    if code not in langcode:
        print('Язык недоступен!')
    else:
        words = text.split()
        mode = input('Выберите режим (замена или выделение): ').lower()
        if mode != 'замена' and mode != 'выделение':
            print('Ошибка! Некорректный ввод!')
        elif mode == 'замена':
            with open(f"{langcode[code]}_corpus.txt", 'r', encoding = 'utf-8') as c:
                with open(f'Текст_исправленный.txt', 'w', encoding = 'utf-8') as f:
                    corpus = set(c.read().split('\n'))
                    for i in range(len(words)):
                        w = re.sub(r'[^A-Za-zĀāĄąČčĒēĘęĖėĢģĪīĮįĶķĻļŅņŠšŪūŲųŽž\s\d]+','', words[i])
                        if w in corpus or w.isalpha() == False:
                            f.write(f"{words[i]} ")
                        else:
                            f.write(f"{re.sub(w, replace_with_correct(words[i], corpus), words[i])} ")
        elif mode == 'выделение':
            ind = input('Выберите тип выделения (полужирный или курсив): ').lower()
            if ind != 'полужирный' and ind != 'курсив':
                print('Ошибка! Некорректный ввод!') # на всякий пожарный защита от дурака
            else:
                with open(f"{langcode[code]}_corpus.txt", 'r', encoding = 'utf-8') as c:
                    with open(f'Ошибки_{ind}.md', 'w', encoding = 'utf-8') as f:
                        corpus = set(c.read().split('\n'))
                        for i in range(len(words)):
                            w = re.sub(r'[^A-Za-zĀāĄąČčĒēĘęĖėĢģĪīĮįĶķĻļŅņŠšŪūŲųŽž\s\d]+','', words[i])
                            if w in corpus or w.isalpha() == False:
                                f.write(f"{words[i]} ")
                            else:
                                f.write(f"{re.sub(w, indicate_wrong(w, ind), words[i])} ")