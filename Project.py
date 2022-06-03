#! python -m pip install pyqt6
#! python -m pip install pyqt-tools
#! python -m pip install langdetect
#! python -m pip install python-Levenshtein

from langdetect import detect
import Levenshtein as lev
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import re, string, sys, warnings
warnings.filterwarnings("ignore")

def replace_with_correct(token, wordlist):
    dist = {}
    for word in wordlist:
        dist[word] = lev.distance(token, word) # ключ -- словоформа из корпуса, значение -- расстояние относительно неправильного токена из пользовательского файла
    optimal_dist = min(list(dist.values()))
    optimal_candidate = [i for i in dist if dist[i] == optimal_dist]
    return optimal_candidate[0] # дубовая замена на первый элемент в списке словоформ с наименьшим расстоянием, из-за точности хочется плакать

def indicate_wrong(token, marker): # тут просто замена токена на тот же токен, окруженный нужными тегами
    indication = {
        'полужирный':'__',
        'курсив':'_'
    }
    res = f'{indication[marker]}{token}{indication[marker]}'
    return res
# ядро через раз перезапускать, но ладно, хрен с ним, работает -- на том спасибо

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Spellchecker")
        
        descript = """Добро пожаловать в наше проектное приложение!
        
Наш спеллчекер позволяет проверить правописание текстов на литовском и латышском языке. Приложение предлагает не только замену слов с опечатками, но и выделение их полужирным или курсивным шрифтом.
        
Все, что Вам необходимо сделать — выбрать режим обработки и загрузить файл с текстом. Принимаются только файлы с расширением .txt в кодировке UTF-8. Если ваш файл не соответствует этим требованиям, пожалуйста, конвертируйте его перед загрузкой.
        
Для начала работы нажмите на кнопку "Mode" в меню.
        
Если у Вас возникнут вопросы или сбои при использовании приложения, нажмите на кнопку "Help", ведущую к справке."""

        label = QLabel(descript) # размещение текста
        label.setWordWrap(True) # переносы, иначе текст улетает за границы окна
        label.setAlignment(Qt.AlignmentFlag.AlignCenter) # выравнивание по центру
        self.setFixedSize(QSize(500, 400)) # фиксированный размер окна
        self.setCentralWidget(label) # текст в центре окна

        button_change = QAction("&Замена", self) # кнопка номер раз
        button_change.setStatusTip("Заменить слово с опечаткой") # понты бессмысленные и беспощадные: всплывающий текст при наведении мыши
        button_change.triggered.connect(self.onTheChangeButtonClick) # что делать, если кнопка нажата

        button_indication = QAction("&Выделение", self) # кнопка номер два
        button_indication.setStatusTip("Выделить слово с опечаткой")
        button_indication.triggered.connect(self.onTheIndicationButtonClick)
        
        button_help = QAction("&Справка", self) # кнопка номер три
        button_help.setStatusTip("Справка")
        button_help.triggered.connect(self.onTheHelpButtonClick)
        
        menu = self.menuBar() # добавляем меню
        file_menu = menu.addMenu("&Mode") # раздел первый, кнопки: замена и выделение
        file_menu.addAction(button_change)
        file_menu.addSeparator() # ну просто прикольный разделитель почему бы и нет
        file_menu.addAction(button_indication)
        file_menu = menu.addMenu("&Help") # раздел второй: кнопки: справка
        file_menu.addAction(button_help)
        
    def onTheChangeButtonClick(self): # если пользователь нажал кнопку замены
        file_upload = QFileDialog.getOpenFileName()[0] # окно для загрузки файла, который хотим проверить
        langcode = {
            'lv':'Latvian',
            'lt':'Lithuanian'
        } # для удобства после распознавания языка: распознавание выдает код языка, а по словарю можно выцеплять первые слова в названиях нужных файлов

        with open(file_upload, 'r', encoding = 'utf-8') as f: # читаем, че там
            text = f.read() # это текст пользователя
            code = detect(text)
            if code not in langcode: # если пользователь не умеет читать стартовые инструкции -- не моя проблема
                dlg = QMessageBox(self) # окно с сообщением об ошибке, если язык не латышский и не литовский
                dlg.setWindowTitle("Error")
                dlg.setText("Ошибка! Язык недоступен!")
                dlg.exec()
            else:
                words = text.split() # токенизация сплитами для сохранения пунктуации
                with open(f"{langcode[code]}_corpus.txt", 'r', encoding = 'utf-8') as c: # открываем НУЖНЫЙ корпус
                    with open(f'Текст_исправленный.txt', 'w', encoding = 'utf-8') as f: # создаем файл для исправлений
                        corpus = set(c.read().split('\n')) # преобразование во множ-во для оптимизации по времени при работе с in
                        for i in range(len(words)):
                            w = re.sub(r'[^A-Za-zĀāĄąČčĒēĘęĖėĢģĪīĮįĶķĻļŅņŠšŪūŲųŽž\s\d]+','', words[i]) # жуткая регулярка отсекает знаки препинания
                            if w in corpus or w.isalpha() == False: # если токен, очищенный от пунктуации, в корпусе, либо это не токен, а цифра -- пишем все, что было до отрезания пунктуации
                                f.write(f"{words[i]} ")
                            else: # заменяем в исходной единице-токене часть без пунктуации на верный варик написания
                                f.write(f"{re.sub(w, replace_with_correct(words[i], corpus), words[i])} ")

                dlg = QMessageBox(self) # окно с сообщением о том, что все супер, вы прекрасны
                dlg.setWindowTitle("Sucсess!")
                dlg.setText("Ваш файл готов!")
                dlg.exec()
                            
    def onTheIndicationButtonClick(self): # если пользователь нажал кнопку выделения
        file_upload = QFileDialog.getOpenFileName()[0] # все то же самое, что при нажатии замены
        langcode = {
            'lv':'Latvian',
            'lt':'Lithuanian'
        }

        with open(file_upload, 'r', encoding = 'utf-8') as f:
            text = f.read() # это текст пользователя
            code = detect(text)
            if code not in langcode: # опять же, не мои проблемы, что пользователь не читает инструкцию
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Error")
                dlg.setText("Ошибка! Язык недоступен!")
                dlg.exec()
            else:
                words = text.split()
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Indication")
                dlg.setText('Напишите тип выделения в консоли\n\nДля этого нажмите на кнопку "Ок"')
# в итоге писать в консоль, потому что не получилось воплотить изначальную задумку с выбором типа нажатием кнопки во всплывающем окне
# я не понимаю, как настроить диалоговое окно с кастомными кнопками, а не стандартными + так, чтобы они давали значение ind
                button = dlg.exec()
                ind = input('Выберите тип выделения (полужирный или курсив): ').lower()
                if ind != 'полужирный' and ind != 'курсив': # на случай, если пользователь не умеет писать
                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("Error")
                    dlg.setText("Ошибка! Некорректный ввод!")
                    dlg.exec()
                else:
                    with open(f"{langcode[code]}_corpus.txt", 'r', encoding = 'utf-8') as c: # открываем корпус
                        with open(f'Ошибки_{ind}.md', 'w', encoding = 'utf-8') as f: # создаем файл для подсветки опечаток
                            corpus = set(c.read().split('\n'))
                            for i in range(len(words)):
                                w = re.sub(r'[^A-Za-zĀāĄąČčĒēĘęĖėĢģĪīĮįĶķĻļŅņŠšŪūŲųŽž\s\d]+','', words[i]) # для поиска по корпусу ремувим пунктуацию
                                if w in corpus or w.isalpha() == False:
                                    f.write(f"{words[i]} ")
                                else:
                                    f.write(f"{re.sub(w, indicate_wrong(w, ind), words[i])} ") # выделение тегами исключительно неправильной части

                    dlg = QMessageBox(self) # окно с сообщением том, что все хорошо
                    dlg.setWindowTitle("Suсcess!")
                    dlg.setText("Ваш файл готов!")
                    button = dlg.exec()

    def onTheHelpButtonClick(self): # справка, если вдруг первичные инструкции проигнорировали
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Help")
# я пока не знаю, чем такое простое приложение может не угодить, так что на случай чего почта разработчика в справке
        to_user = """Добро пожаловать в справку!
        
Какие вопросы могут возникнуть у Вас?
        
        Вопрос: Почему программа не работает с моим файлом?
        Ответ: Проблема может быть связана либо с языком текста, либо с форматом файла. В случае проблемы первого типа убедитесь, что текст написан на литовском или латышском языке (программа не поддерживает иные языки). Во втором случае конвертируйте файл, который хотите проверить в формат txt.
        
        Вопрос: Программа считает слово неправильным, а я думаю иначе. Как сказать программе, что это правильное слово?
        Ответ: Запустите программу заново в режиме добавления словоформ.
        
        Вопрос: Почему слова не заменяются, либо заменяются, но не так, как я хочу?
        Ответ: Приложение работает без учета контекста, поэтому алгоритм сам выбирает приемлемый вариант, который может не совпадать с Вашей интуицией.
        
Надеемся, мы помогли вам! Если остались вопросы, обращайтесь по почте: aagolovina_2@edu.hse.ru"""
        
        dlg.setText(to_user)
        dlg.exec()

app = QApplication(sys.argv) # собственно вывод окна
window = MainWindow()
window.show()
app.exec()