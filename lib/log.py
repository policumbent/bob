class log:
    @staticmethod
    def err(msg):
        print(f"\033[1;32 [ERR] {msg}")

    @staticmethod
    def warn(msg):
        print(f"\033[1;33 [WARN] {msg}")

    @staticmethod
    def info(msg):
        print(f"[INFO] {msg}")