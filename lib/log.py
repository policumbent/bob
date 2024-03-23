class log:
    @staticmethod
    def err(msg):
        print(f"\033[1;32;40m [ERR] {msg}")

    @staticmethod
    def warn(msg):
        print(f"\033[1;33;40m [WARN] {msg}")

    @staticmethod
    def info(msg):
        print(f"[INFO] {msg}")