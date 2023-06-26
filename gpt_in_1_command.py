import json  # импортируем модуль json для работы с JSON-данными
import requests  # импортируем модуль requests для отправки HTTP-запросов
from translate import Translator  # импортируем модуль Translator из библиотеки googletrans для перевода текста
import subprocess  # импортируем модуль subprocess для выполнения команд в терминале
import os  # импортируем модуль os для работы с операционной системой
import platform  # импортируем модуль platform для получения информации о системе

translator = Translator(to_lang='en', from_lang='ru')  # создаем объект Translator для перевода текста на английский язык

# Создаем переменную prompt с информацией о системе и ограничениях
prompt = """Main task is: Create a test file.
Assistant: {'name', 'execute_shell', 'args': 'touch test'}""" + f"""System:
Behavior:
    You are an AI console and should return commands based on what the user presented to you in the text view.
System information:
    System: {platform.uname()[0]}
    Node: {platform.uname()[1]}
    Current user: {os.getlogin()}""" + """
Limitations:
    Remember that if you are running on a linux system, you must use the package manager of that distribution to install the python libraries, not pip.
    You have no files and you have to create them or search for them yourself (on linux it is find -name "file name or part of it", on windows dir <disk to search> /s | find /i "<your text>").
    For 1 answer you can use only 1 command.
    No help from the user and no questions to the user.
Answer format:
    Commands (use only them):
        1. execute_shell: execute command in shell and return result, name: "execute_shell", args: "console command"
    The format of the response should be a json example of which will be given below:
    JSON response format:
        {"name" : "here is the name of command", "args": "here is the args"}
    Make sure your response can be read with json.loads().
Be sure to answer ONLY in JSON format."""

# Функция для отправки запроса на сервер и получения ответа
def ask(prompt):
    # Подготавливаем данные для запроса
    data = {
        "prompt": prompt
    }
    payload = json.dumps(data)
    # Устанавливаем заголовки
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Origin": "https://chatbot.theb.ai",
        "Referer": "https://chatbot.theb.ai/"
    }
    url = "https://chatbot.theb.ai/api/chat-process"
    response = requests.post(url, data=payload, headers=headers)
    response_text = response.text
    json_strings = response_text.strip().split('\n')
    last_json_string = json_strings[-1]
    response_json = json.loads(last_json_string)
    return response_json['text']

# Переводим введенный пользователем текст на английский язык
SafeInput = translator.translate(input("Введите задачу >> "))
# Создаем переменную endPrompt с информацией о системе и введенной пользователем задаче
endPrompt = prompt+"\nMain task is: "+SafeInput
try:
    # Запрашиваем ответ от сервера
    out1 = ask(endPrompt)
    # Извлекаем из ответа JSON-строку
    start = out1.find("{") + 1
    end = out1.find("}") + 1
    out = "{" + out1[start:end]
    print(out)
    status = input('Вы подтверждаете выполнение данной команды (y/n)? >> ')
    if status == 'y':
        # Извлекаем из JSON-строки имя команды
        command = json.loads(out)['name']
        # Если команда - execute_shell, выполняем команду в терминале
        if command == "execute_shell":
            os.system(json.loads(out)['args']
        else:
            print('Неизвестная команда от gpt...')
    else:
        print("Ничего не сделано...")
# Обрабатываем исключение ChunkedEncodingError
except requests.exceptions.ChunkedEncodingError:
    print("Ошибка запроса, попробуйте еще раз.")
print("Done.")
