class MexPriority:
    very_low = 1
    low = 2
    medium = 3
    high = 4
    very_high = 5


class MexType:
    default = 0
    trap = 1


class Message:
    def __init__(self, text: str, message_priority: MexPriority, message_type: MexType, time: int,  timeout: int):
        self.text = text
        self.message_priority = message_priority
        self.message_type = message_type
        self.time = time
        self.timeout = timeout

    @property
    def values(self):
        return {
            'text': self.text,
            'message_priority': self.message_priority,
            'message_type': self.message_type,
            'time': self.time,
            'timeout': self.timeout
        }
