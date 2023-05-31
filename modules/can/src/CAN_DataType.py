CAN_DATA_TYPE_LIST = [
    "speed",
    "distance",
    "rpm",
    "power",
    "heart_rate",
    "gear",
    "gear_status",
    #"accelerometer",
    #"air_quality",
]


class CAN_DataType:
    def __init__(self, dlc, decimal_digits):
        self.dlc = dlc
        self.decimal_digits = decimal_digits


CAN_DATA_TYPE = {
    "speed":        CAN_DataType(dlc = 2, decimal_digits = 2),
    "distance":     CAN_DataType(dlc = 2, decimal_digits = 0),
    "rpm":          CAN_DataType(dlc = 2, decimal_digits = 1),
    "power":        CAN_DataType(dlc = 2, decimal_digits = 1),
    "heart_rate":   CAN_DataType(dlc = 1, decimal_digits = 0),
    "gear":         CAN_DataType(dlc = 1, decimal_digits = 0),
    "gear_status":  CAN_DataType(dlc = 1, decimal_digits = 0),
    #"accelerometer":,
    #"air_quality":,
}