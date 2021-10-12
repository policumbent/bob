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
    def __init__(
            self,
            text: str,
            message_priority: int = MexPriority.medium,
            message_type: int = MexType.default,
            message_time: int = 5,
            message_timeout: int = 10):
        self.text = text
        self.message_priority = message_priority
        self.message_type = message_type
        self.message_time = message_time
        self.message_timeout = message_timeout

    @property
    def values(self):
        return {
            'text': self.text,
            'message_priority': self.message_priority,
            'message_type': self.message_type,
            'message_time': self.message_time,
            'message_timeout': self.message_timeout
        }

    def __cmp__(self, other):
        return self.message_priority - other.message_priority

    def __lt__(self, other):
        return self.get_priority() < other.get_priority()

    def reduce_time(self):
        self.message_time -= 1
        return self.message_time

    def to_str(self):
        return self.text + " T:" + str(self.message_time) + " P:" + str(self.message_priority) + " Timeout: " + str(self.message_timeout)

    def get_priority(self):
        return self.message_priority

    def get_timeout(self):
        return self.message_timeout

    def reduce_timeout(self):
        if self.message_timeout > 0:
            self.message_timeout -= 1
        return

