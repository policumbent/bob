from datetime import datetime
import can


def entry_point():
    date = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')

    with open(f"can_{date}.log", "w") as log_file:
        curr_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"{curr_time}\n")

    bus = can.Bus(interface = 'socketcan',
        channel = 'can0',
        receive_own_messages = True)


if __name__ == '__main__':
    entry_point()