# Не пиздите код плеееез.




import json  # импортируем модуль json для работы с JSON-данными
import requests  # импортируем модуль requests для отправки HTTP-запросов
from translate import Translator  # импортируем модуль Translator из библиотеки googletrans для перевода текста
import subprocess  # импортируем модуль subprocess для выполнения команд в терминале
import os  # импортируем модуль os для работы с операционной системой
import platform  # импортируем модуль platform для получения информации о системе

translator = Translator(to_lang='en', from_lang='ru')  # создаем объект Translator для перевода текста на английский язык

# Создаем переменную prompt с информацией о системе и ограничениях
prompt = """Main task is: Create a test file.
Assistant: {'name', 'execute_shell', 'args': 'touch test'}
User: Success.
Assistant: {'name', 'end', 'args': 'task complete successful'}
Main task is: """ + f"""
System:
Behavior:
    You are an AI console and should return commands based on what the user presented to you in the text view.
    After completing the main task, you must complete the work of.
System information:
    System: {platform.uname()[0]}
    Node: {platform.uname()[1]}
    Current user: {os.getlogin()}""" + """
Limitations:
    Remember that if you are running on a linux system, you must use the package manager of that distribution to install the python libraries, not pip.
    You have no files and you have to create them or search for them yourself (on linux it is find -name "file name or part of it", on windows dir <disk to search> /s | find /i "<your text>").
    If you have completed the task, you MUST use the "end" command.
    Your maximum is 5 commands, use them wisely.
    For 1 answer you can use only 1 command.
    If you finish a task before you use these 5 commands, use the "end" command.
    Use the LOWEST number of commands.
    No help from the user and no questions to the user.
Answer format:
    Commands (use only them):
        1. execute_shell: execute command in shell and return result, name: "execute_shell", args: "console command"
        2. end: finishes the job, if you have done the main task you are obliged to use this command, name: "end", args: "task result"
    The format of the response should be a json example of which will be given below:
    JSON response format:
        {"name" : "here is the name of command", "args": "here is the args"}
    Make sure your response can be read with json.loads().
Be sure to answer ONLY in JSON format.
After completing the main task, you must complete the work of."""

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
# Цикл для выполнения команд пользователя
for i in range(5):
    try:
        # Запрашиваем ответ от сервера
        out1 = ask(endPrompt)
        # Извлекаем из ответа JSON-строку
        start = out1.find("{") + 1
        end = out1.find("}") + 1
        out = "{" + out1[start:end]
        if out == "{":
            print(out1)
        print("Command number " + str(i+1))
        print(out)
        status = input('Вы подтверждаете выполнение данной команды (y/n)? >> ')
        if status == 'y':
            # Извлекаем из JSON-строки имя команды
            command = json.loads(out)['name']
            # Выводим номер команды
            # Если команда - execute_shell, выполняем команду в терминале
            if command == "execute_shell":
                output = subprocess.run(json.loads(out)['args'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True).stdout
                # Добавляем результат выполнения команды в переменную endPrompt
                endPrompt += "\nAssistant: " + out + "\nUser: " + output
                # Если команда выполнена успешно, выводим сообщение об успехе
                if output == "":
                    if 5-i != 1:
                        endPrompt += "User: Success. Commands left: " + str(5-i)
                    else:
                        endPrompt += "User: Success. Commands left: " + str(5-i) + '. Last command!'
            # Если команда - end, завершаем выполнение цикла
            elif command == 'end':
                print(json.loads(out)['args'])
                break
        else:
            print('Пропуск команды...')
    # Обрабатываем исключение ChunkedEncodingError
    except requests.exceptions.ChunkedEncodingError:
        pass
