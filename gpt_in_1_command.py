#импорты
from os import getlogin, system
import platform
import json  
import requests 
from translate import Translator

# Переводчики
translator = Translator(to_lang='en', from_lang='ru')
translatorToRu = Translator(to_lang='ru', from_lang='en')

# Основной промт для GPT для генерации команд
prompt = """Main task is: Create a test file.
Assistant: {'name', 'execute_shell', 'args': 'touch test'}""" + f"""System:
Behavior:
    You are an AI console and should return commands based on what the user presented to you in the text view.
System information:
    System: {platform.uname()[0]}
    Node: {platform.uname()[1]}
    Current user: {getlogin()}""" + """
Limitations:
    Remember that if you are running on a linux system, you must use the package manager of that distribution to install the python libraries, not pip.
    You have no files and you have to create them or search for them yourself (on linux it is find -name "file name or part of it", on windows dir <disk to search> /s | find /i "<your text>").
    For 1 answer you can use only 1 command.
    Always close such signs as " {.
    Do not use single quotes ('), only double quotes (").
    Before using any utilities, try to install them on the PC.
    No help from the user and no questions to the user.
Answer format:
    Commands (use only them):
        1. "name": "execute_shell", execute command in shell and return result, args: "console command"
    The format of the response should be a json example of which will be given below:
    JSON response format:
        {"name" : "here is the name of command", "args": "here is the args"}
    Make sure your response can be read with json.loads(). """+f"""
Make sure your console command is for the OS {platform.uname()[0]} {platform.uname()[1]}.
Be sure to answer ONLY in JSON format."""

#Предупреждение
if platform.uname()[0].lower() == 'windows':
    print("Внимание!!! Для корректной установки доп. утилит на Windows у вас должен быть установлен пакетный менедежр choco и утилита git (желательно)....")

# Функция для отправки запроса на сервер и получения ответа
def ask(prompt):
    data = {
        "prompt": prompt
    }
    payload = json.dumps(data)
    
    # Заголовки запроса
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
    
    #обработка ответа от API
    responseText = response.text
    jsonStrings = responseText.strip().split('\n')
    lastJsonString = jsonStrings[-1]
    responseJson = json.loads(lastJsonString)
    
    return responseJson['text']

# Переводим введенный пользователем текст на английский
safeInput = translator.translate(input("Введите задачу >> "))

# Объединение текста
endPrompt = prompt+"\nMain task is: "+safeInput

try:
    # Ответ от GPT
    out1 = ask(endPrompt)
    
    # Извлечение JSON из ответа
    start = out1.find("{")
    end = out1.rfind("}") + 1
    out = out1[start:end]
    print(out)
    
    status = input('Вы подтверждаете выполнение данной команды (y/n)? >> ')
    
    # Выполнение команды
    if status == 'y':
        
        # Извлекаем имя команды
        command = json.loads(out)['name']
        
        # Промт для установки зависимостей.
        promptForUtil = """User: command: git clone https://github.com/mchlebushec/gpt_in_terminal. Windows 10 OS.
Assistant: {"command": "install", "args": "choco install git.install --params "'/GitAndUnixToolsOnPath /WindowsTerminal /NoAutoCrlf'""}
User: command: pwd. Arch linux OS.
Assistant: {"command": "system", "args": "any text"}
User: command: git clone https://github.com/mchlebushec/gpt_in_terminal. Arch linux OS.
Assistant: {"command": "install", "args": "sudo pacman -S git"}
System:
    Behavior:
        you are the AI that determines if a utility is system utility by a command from the terminal. you will be sent a terminal and OS command, and you answer either "yes, it is system", or "no, here is a one line command to install it: (here command without brackets)", or "I cannot install utility <name of utility without quotation marks>".
    Limitations:
        to install utilities on Linux, use the package manager (built-in).
        To install utilities on Windows use the choco package manager or the git utility.
        Do not use single quotes ('), only double quotes (").
    Commands:
        1) "command" "system", means you can execute without installing utilities, "args": "any text"
        2) "command": "install", means you know the command to install the utility, "args": "command to install"
        3) "command": "cannot", means you can't install it yourself in terminal (even if the utility is installed by default on the system you still shouldn't use this command unless you can't install the utility), "args": "any text"
    Answer format:
        you answer only in the john format below:
            {"command": "command name", "args": "command argument"}
        Make sure your response can be read with json.loads() in python."""
        
        # Объединение текстов и запрос к GPT
        commandInstallStatus = ask(promptForUtil + "\nUser: command: " + json.loads(out)['args'] + ". " + platform.uname()[0] + " " + platform.uname()[1] + " OS")
        
        # Извлечение JSON
        commandInstallStatus = json.loads(commandInstallStatus[commandInstallStatus.find("{"):commandInstallStatus.rfind("}")+1])
        
        #Проверка нужны ли зависимости
        if commandInstallStatus['command'] == 'system':
            # Не нужны
            print("Команда является системной, продолжение работы.")
        
        elif commandInstallStatus['command'] == 'install':
            # Зависимости нужны, попытка установить утилиту.
            confirmation = input("Утилита используемая в команде не является системной, команда для установки: '" + commandInstallStatus['args'] + "'. подтверждаете ее установку? (y/n) >> ")
            
            if confirmation == 'y':
                print("Запуск установки утилиты....")
                system(command_install_status['args'])
                print("Установка завершена! ")
            
            elif confirmation == 'n':
                print("Пропуск установки уилиты....")
                print("ВНИМАНИЕ! Основная команда может не сработать!")
        
        elif commandInstallStatus['command'] == 'cannot':
            # Зависимости нужны но бот не может их установить самостоятельно
            status = input("Сожалеем, но программа не может установить утилиту используемую в команде. Установлена ли утилита для данной команды? (y/n) >> ")
            
            # Проверка установлена ли утилита
            if status == 'y':
                print("Утилита установлена, продолжение работы....")
            
            elif status == 'n':
                print("Утилита не установлена, могут возникнуть ошибки в процессе выполнения команды....")
        
        # Выполняем команду в терминале
        if command == "execute_shell":
            system(json.loads(out)['args'])
        
        else:
            print('Неизвестная команда от gpt...')
    
    else:
        print("Ничего не сделано...")

# Обрабатываем исключение в случае ошибки в ходе получения овтета от GPT
except requests.exceptions.ChunkedEncodingError:
    print("Ошибка запроса, попробуйте еще раз.")

print("Done.")
