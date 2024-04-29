class log:
    @staticmethod
    def err(msg):
        print(f"\033[1;31m [ERR] {msg}\033[0;37m")

    @staticmethod
    def warn(msg):
        print(f"\033[1;33m [WARN] {msg}\033[0;37m")

    @staticmethod
    def info(msg):
        print(f"[INFO] {msg}")