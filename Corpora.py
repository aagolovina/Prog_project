# to check actual date of a dump: https://dumps.wikimedia.org/backup-index.html
#! python -m pip install apache_beam mwparserfromhell
#! python -m pip install datasets
#! python -m pip install langdetect

#from langdetect import detect
from datasets import load_dataset
import re, string

lv_alphabet = re.compile(r'^[A-Za-zĀāČčĒēĢģĪīĶķĻļŅņŠšŽž]+$')
lt_alphabet = re.compile(r'^[A-Za-zĄąČčĘęĖėĮįŠšŲųŪūŽž]+$')

def create_wordlist(data, lang, lang_code, alphabet):                     # data = дамп из википедии, alphabet = re.compile-строка
    text = ' '.join(data)
    text = re.sub(r'[0-9]', '', text)                                     # удаление чисел
    text = text.translate(str.maketrans('', '', string.punctuation))      # удаление пунктуации
    text = [i for i in text.split() if re.search(alphabet, i) != None]    # удаление слов, в которых содержится что-либо, кроме букв
#    text = [word for word in text if detect(word) == lang_code]          # удаление слов из других языков (замедляет работу программы ровно на 6 часов)

    wordlist = set(text) # удаление дубликатов + оптимизация по времени при работе с оператором in

    print(f'{lang} corpus consists of {len(wordlist)} word forms')

    with open(f"{lang}_corpus.txt", "w", encoding="utf-8") as f:
        for word in wordlist:
            f.write(word)
            f.write('\n')
            
lv_data = load_dataset("wikipedia", language="lv", date="20220401", beam_runner='DirectRunner')['train']['text']
lt_data = load_dataset("wikipedia", language="lt", date="20220401", beam_runner='DirectRunner')['train']['text']
#ltg_data = load_dataset("wikipedia", language="ltg", date="20220420", beam_runner='DirectRunner')['train']['text']
# латгальский в пролете, его нет в langdetect(((

create_wordlist(lv_data, 'Latvian', 'lv', lv_alphabet)
create_wordlist(lt_data, 'Lithuanian', 'lt', lt_alphabet)
#create_wordlist(ltg_data, 'Latgalian', 'ltg', r'^[A-Za-zĀāČčĒēĢģĪīĶķĻļŅņŌōŠšŪūŽž]+$')
# работает очень долго, на каждый датасет примерно по полчаса, так что этот кусок кода просто запустить, помолиться и оставить в покое на весь день