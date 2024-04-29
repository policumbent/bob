import os


def home_path():
    return os.getenv("HOME")


def db_path():
    return os.getenv("DATABASE_PATH") or default_db_path()


def default_db_path():
    return f"{home_path()}/bob/database.db"


def default_recording_path():
    return f"{home_path()}/bob/onboard_video"