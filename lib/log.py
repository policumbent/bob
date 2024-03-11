from colorama import Fore, init

init(autoreset=True)


class log:
    @staticmethod
    def err(msg):
        print(Fore.RED + f"[ERR] {msg}")

    @staticmethod
    def warn(msg):
        print(Fore.YELLOW + f"[WARN] {msg}")

    @staticmethod
    def info(msg):
        print(Fore.WHITE + f"[INFO] {msg}")