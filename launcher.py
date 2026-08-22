import os
import sys
import ctypes
import threading
import subprocess
from colorama import init, Fore, Style
from core import DpiEngine

init(autoreset=True)

BANNER = f"""{Fore.RED}
 ____             _            ____                  
| __ ) _ __ __ _ | |_ __   __ / ___|_ __ __ _ _ __ ___  
|  _ \| '__/ _` || __|\ \ / /| |  _| '__/ _` | '_ ` _ \ 
| |_) | | | (_| || |_  \ V / | |_| | | | (_| | | | | | |
|____/|_|  \__,_| \__|  \_/   \____|_|  \__,_|_| |_| |_|
{Fore.YELLOW}  >> Portable Telegram + Built-in Anti-DPI Core <<{Style.RESET_ALL}
"""

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def elevate_privileges():
    params = f'"{os.path.abspath(sys.argv[0])}"'
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def main():
    print(BANNER)

    if not is_admin():
        print(f"{Fore.YELLOW}[*] Запрос прав Администратора для сетевого драйвера...{Style.RESET_ALL}")
        elevate_privileges()
        sys.exit(0)

    base_dir = get_base_dir()
    tg_exe = os.path.join(base_dir, "Telegram", "Telegram.exe")

    if not os.path.exists(tg_exe):
        print(f"{Fore.RED}[Ошибка] Telegram.exe не найден по пути: {tg_exe}{Style.RESET_ALL}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    print(f"{Fore.GREEN}[1/2] Запуск службы обхода блокировок (BratvaDPI)...{Style.RESET_ALL}")
    engine = DpiEngine(split_pos=2, fake_ttl=3)
    dpi_thread = threading.Thread(target=engine.start, daemon=True)
    dpi_thread.start()

    print(f"{Fore.GREEN}[2/2] Запуск Telegram Desktop...{Style.RESET_ALL}")
    
    try:
        process = subprocess.Popen([tg_exe], cwd=os.path.join(base_dir, "Telegram"))
        print(f"{Fore.CYAN}[✓] Все системы активны. Telegram работает без ограничений.{Style.RESET_ALL}")
        print("[i] Закройте Telegram, чтобы остановить службу.\n")
        process.wait()
    except Exception as e:
        print(f"{Fore.RED}[!] Ошибка запуска Telegram: {e}{Style.RESET_ALL}")
    finally:
        print(f"{Fore.YELLOW}[*] Выгрузка драйвера обхода...{Style.RESET_ALL}")
        engine.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
