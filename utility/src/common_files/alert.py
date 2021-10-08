class AlertPriority:
    very_low = 1
    low = 2
    medium = 3
    high = 4
    very_high = 5


class Alert:
    def __init__(
            self,
            text: str,
            alert_priority: int):
        self.text = text
        self.alert_priority = alert_priority

    @property
    def values(self):
        return {
            'text': self.text,
            'alert_priority': self.alert_priority
        }
