from datetime import datetime
import can

FILE_NAME = f"can_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.log"

def entry_point():
    with open(FILE_NAME, "w") as log_file:
        curr_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"{curr_time}\n")

    bus = can.Bus(interface = 'socketcan',
        channel = 'can0',
        receive_own_messages = True)

    logger = can.Logger(FILE_NAME, 'w')


if __name__ == '__main__':
    entry_point()