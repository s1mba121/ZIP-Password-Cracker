import zipfile
import rarfile
import py7zr
import itertools
import string
from concurrent.futures import ThreadPoolExecutor
import time
import os
import argparse
from tqdm import tqdm  # библиотека для прогресс-бара

ascii_art = r"""
         _nnnn_                      
        dGGGGMMb
       @p~qp~~qMb
       M|@||@) M|
       @,----.JM|
      JS^\__/  qKL
     dZP        qKRb
    dZP          qKKb
   fZP            SMMb
   HZM  s1mba121  MMMM
   FqM            MMMM
 __| ".        |\dS"qML
 |    `.       | `' \Zq
_)      \.___.,|     .'
\____   )MMMMMM|   .'
     `-'       `--'
     
🔒 ZIP Password Cracker 🔒
"""

print(ascii_art)

# Настройка аргументов командной строки
parser = argparse.ArgumentParser(description="Bruteforce Archive Password Cracker")
parser.add_argument("archive_file", help="Имя архива для взлома")
parser.add_argument("-n", "--numeric", action="store_true", help="Использовать только цифры для перебора пароля")
parser.add_argument("-c", "--cluster", action="store_true", help="Активировать режим кластера")
parser.add_argument("--total-nodes", type=int, help="Общее количество узлов в кластере (только в режиме кластера)")
parser.add_argument("--node-index", type=int, help="Индекс текущего узла в кластере (начиная с 0)")
parser.add_argument("--d", "--debug", action="store_true", help="Режим отладки: выводит каждый пробуемый пароль")
parser.add_argument("-f", "--password-file", type=str, help="Путь к файлу со списком паролей")
parser.add_argument("--lang", choices=["ru", "en"], default="en", help="Выбор языка интерфейса (ru или en)")
args = parser.parse_args()

archive_file = args.archive_file
use_numeric_only = args.numeric
use_cluster_mode = args.cluster
debug_mode = args.d
total_nodes = args.total_nodes
node_index = args.node_index
password_file = args.password_file
language = args.lang

# Сообщения на русском и английском языках
messages = {
    "en": {
        "cluster_error": "In cluster mode, --total-nodes and --node-index must be specified.",
        "node_index_error": "Node index must be between 0 and total_nodes - 1.",
        "cluster_mode": "⚙️ Cluster mode enabled: Node {}/{}",
        "default_mode": "⚙️ Default mode enabled",
        "welcome": "🔐 Welcome to the Bruteforce Archive Password Cracker 🔐\n",
        "unsupported_format": "Unsupported archive format!",
        "enter_min_length": "Enter minimum password length (0 to start from 1): ",
        "invalid_min_length": "Invalid value for minimum password length.",
        "enter_max_length": "Enter maximum password length (0 for infinite): ",
        "invalid_max_length": "Invalid value for maximum password length.",
        "password_found": "\n[+] Password found: {}",
        "password_saved": "Password saved to file: {}",
        "password_file_read": "🔍 Reading passwords from file: {}",
        "bruteforce_complete": "\n💀 Bruteforce complete 💀",
        "trying_length": "\n🚀 Trying length of {} characters...",
        "bruteforce_start": "Starting bruteforce...\n",
        "time_elapsed": "Time: {:.2f} sec",
        "process": "Process"
    },
    "ru": {
        "cluster_error": "В режиме кластера необходимо указать --total-nodes и --node-index.",
        "node_index_error": "Индекс узла должен быть от 0 до total_nodes - 1.",
        "cluster_mode": "⚙️ Запущен кластерный режим: Узел {} из {}",
        "default_mode": "⚙️ Запущен обычный режим",
        "welcome": "🔐 Добро пожаловать в Bruteforce Archive Password Cracker 🔐\n",
        "unsupported_format": "Неподдерживаемый формат архива!",
        "enter_min_length": "Введите минимальную длину пароля (0 для начала с 1): ",
        "invalid_min_length": "Некорректное значение для минимальной длины пароля.",
        "enter_max_length": "Введите максимальную длину пароля (0 для бесконечности): ",
        "invalid_max_length": "Некорректное значение для максимальной длины пароля.",
        "password_found": "\n[+] Пароль найден: {}",
        "password_saved": "Пароль сохранен в файл: {}",
        "password_file_read": "🔍 Чтение паролей из файла: {}",
        "bruteforce_complete": "\n💀 Брутфорс завершен 💀",
        "trying_length": "\n🚀 Пробуем длину {} символов...",
        "bruteforce_start": "Начинаем брутфорс...\n",
        "time_elapsed": "Время: {:.2f} сек",
        "process": "Процесс"
    }
}

# Выбор языка
msg = messages[language]

# Проверка и отображение режима работы
if use_cluster_mode:
    if total_nodes is None or node_index is None:
        print(msg["cluster_error"])
        exit(1)
    if node_index < 0 or node_index >= total_nodes:
        print(msg["node_index_error"])
        exit(1)
    print(msg["cluster_mode"].format(node_index + 1, total_nodes))
else:
    print(msg["default_mode"])

print(msg["welcome"])

# Задаем наборы символов
digit_charset = string.digits
full_charset = string.ascii_lowercase + string.digits

# Запрашиваем минимальную и максимальную длину пароля, если не используется файл
if password_file is None:
    try:
        min_length = int(input(msg["enter_min_length"]))
        if min_length == 0:
            min_length = 1
    except ValueError:
        print(msg["invalid_min_length"])
        exit(1)

    try:
        max_length = int(input(msg["enter_max_length"]))
    except ValueError:
        print(msg["invalid_max_length"])
        exit(1)

file_extension = os.path.splitext(archive_file)[1].lower()

def save_password_to_file(password):
    filename = f"{os.path.splitext(archive_file)[0]}_password.txt"
    with open(filename, "w") as f:
        f.write(password)
    print(msg["password_saved"].format(filename))

def try_zip(password):
    try:
        with zipfile.ZipFile(archive_file) as zf:
            zf.extractall(pwd=password.encode('utf-8'))
            print(msg["password_found"].format(password))
            save_password_to_file(password)
            return True
    except (RuntimeError, zipfile.BadZipFile):
        return False

def try_rar(password):
    try:
        with rarfile.RarFile(archive_file) as rf:
            rf.extractall(pwd=password)
            print(msg["password_found"].format(password))
            save_password_to_file(password)
            return True
    except (rarfile.BadRarFile, rarfile.PasswordRequired, rarfile.RarCannotExec):
        return False

def try_7z(password):
    try:
        with py7zr.SevenZipFile(archive_file, mode='r', password=password) as zf:
            zf.extractall()
            print(msg["password_found"].format(password))
            save_password_to_file(password)
            return True
    except (py7zr.Bad7zFile, py7zr.PasswordRequired, py7zr.ArchiveError):
        return False

if file_extension == '.zip':
    try_password = try_zip
elif file_extension == '.rar':
    try_password = try_rar
elif file_extension == '.7z':
    try_password = try_7z
else:
    print(msg["unsupported_format"])
    exit(1)

# Функция для брутфорса с использованием файла паролей
def bruteforce_from_file():
    with open(password_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        total_passwords = len(lines)
        start_time = time.time()
        
        with tqdm(total=total_passwords, desc=msg["process"]) as pbar:
            with ThreadPoolExecutor() as executor:
                for i, line in enumerate(lines):
                    password = line.strip()

                    if use_cluster_mode and i % total_nodes != node_index:
                        continue

                    if debug_mode:
                        print(f"[DEBUG] Trying password: {password}")

                    future = executor.submit(try_password, password)
                    if future.result():
                        executor.shutdown(wait=False)
                        pbar.close()
                        return True
                    
                    pbar.update(1)

                elapsed_time = time.time() - start_time
                pbar.set_postfix({msg["time_elapsed"]: f"{elapsed_time:.2f} сек"})

# Функция для перебора всех возможных паролей
def bruteforce():
    length = min_length
    charset = digit_charset if use_numeric_only else full_charset

    while max_length == 0 or length <= max_length:
        print(msg["trying_length"].format(length))
        combinations = itertools.product(charset, repeat=length)
        total_combinations = sum(1 for _ in itertools.product(charset, repeat=length))
        start_time = time.time()

        with tqdm(total=total_combinations, desc=f"{msg['process']} {length}") as pbar:
            with ThreadPoolExecutor() as executor:
                for i, password_tuple in enumerate(combinations):
                    password = ''.join(password_tuple)

                    if use_cluster_mode and i % total_nodes != node_index:
                        continue

                    if debug_mode:
                        print(f"[DEBUG] Trying password: {password}")

                    future = executor.submit(try_password, password)
                    if future.result():
                        executor.shutdown(wait=False)
                        pbar.close()
                        return True

                    pbar.update(1)

                elapsed_time = time.time() - start_time
                pbar.set_postfix({msg["time_elapsed"]: f"{elapsed_time:.2f} сек"})
                
        length += 1

# Основной процесс взлома
print(msg["bruteforce_start"])
if password_file:
    print(msg["password_file_read"].format(password_file))
    result = bruteforce_from_file()
else:
    result = bruteforce()

if not result:
    print(msg["bruteforce_complete"])
