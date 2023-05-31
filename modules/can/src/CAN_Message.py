import CAN_ID as CID
from CAN_DataType import CAN_DATA_TYPE

from topics import topic_dict, topics

class CAN_Message:
    def __init__(self, enc_id = 0, enc_pl = 0):
        self.enc_id = enc_id
        self.enc_pl = enc_pl

    def __init__(self, topic = "", data = 0):
        self.topic = topic
        self.data = data

        if (topic == topic_dict["hall_speed"]):
            return self._enc_speed(self.data)
        
        if (topic == topic_dict["hall_distance"]):
            return self._enc_distance(self.data)

        if (topic == topic_dict["hall_wheel_rpm"]):
            return self._enc_wheel_rpm(self.data)

        if (topic == topic_dict["srm_pedal_rpm"]):
            return self._enc_pedal_rpm(self.data)

        if (topic == topic_dict["srm_power"]):
            return self._enc_power(self.data)

        if (topic == topic_dict["heartrate"]):
            return self._enc_heartrate(self.data)
        
        return 0, 0

    ###############################################
    ################ DATA ENCODING ################
    ###############################################

    def _encode_data(self, data, dlc, decimal_digits):
        """
        rounding data function
        :param data: data to be rounded
        :param dlc: number of bytes of the resulting ByteArray
        :param decimal_digits: number of input decimal digits
        :return encoded_data: ByteArray
        """

        rounded_data = int(round(data, decimal_digits) * 10**decimal_digits)

        encoded_data = bytearray([])
        for i in range (dlc - 1, -1, -1):
            encoded_data.append((rounded_data & (0xff << (i * 8))) >> (i * 8))

        return encoded_data

    
    def _enc_speed(self, speed):
        """
        encodes speed in ByteArray format
        :param speed
        :return id -> int, encoded_speed -> ByteArray
        """

        id = (CID.MSG_DATA << 9) | (CID.DEV_RPI_DATA << 5) | (CID.RPI_HS_SPEED)

        encoded_speed = self._encode_data(
            speed,
            CAN_DATA_TYPE["speed"].dlc,
            CAN_DATA_TYPE["speed"].decimal_digits
        )

        return id, encoded_speed
    

    def _enc_distance(self, distance):
        """
        encodes distance in ByteArray format
        :param distance
        :return id -> int, encoded_distance -> ByteArray
        """
        id = (CID.MSG_DATA << 9) | (CID.DEV_RPI_DATA << 5) | (CID.RPI_HS_DISTANCE)

        encoded_distance = self._encode_data(
            distance,
            CAN_DATA_TYPE["distance"].dlc,
            CAN_DATA_TYPE["distance"].decimal_digits
        )

        return id, encoded_distance


    def _enc_wheel_rpm(self, rpm):
        """
        encodes rpm in ByteArray format
        :param rpm
        :return id -> int, encoded_rpm -> ByteArray
        """

        id = (CID.MSG_DATA << 9) | (CID.DEV_RPI_DATA << 5) | (CID.RPI_HS_W_RPM)

        encoded_rpm = self._encode_data(
            rpm,
            CAN_DATA_TYPE["rpm"].dlc,
            CAN_DATA_TYPE["rpm"].decimal_digits    
        )

        return id, encoded_rpm


    def _enc_pedal_rpm(self, rpm):
        """
        encodes rpm in ByteArray format
        :param rpm
        :return id -> int, encoded_rpm -> ByteArray
        """

        id = (CID.MSG_DATA << 9) | (CID.DEV_RPI_DATA << 5) | (CID.RPI_SRM_P_RPM)

        encoded_rpm = self._encode_data(
            rpm,
            CAN_DATA_TYPE["rpm"].dlc,
            CAN_DATA_TYPE["rpm"].decimal_digits
        )

        return id, encoded_rpm

    
    def _enc_power(self, power):
        """
        encodes power in ByteArray format
        :param power
        :return id -> int, encoded_power -> ByteArray
        """

        id = (CID.MSG_DATA << 9) | (CID.DEV_RPI_DATA << 5) | (CID.RPI_SRM_PWR)

        encoded_power = self._encode_data(
            power,
            CAN_DATA_TYPE["power"].dlc,
            CAN_DATA_TYPE["power"].decimal_digits
        )

        return id, encoded_power


    def _enc_heartrate(self, heart_rate):
        """
        encodes heart_rate in ByteArray format
        :param heart_rate
        :return id -> int, encoded_hr -> ByteArray
        """

        id = (CID.MSG_DATA << 9) | (CID.DEV_RPI_DATA << 5) | (CID.RPI_HEART_RATE)

        encoded_hr = self._encode_data(
            heart_rate,
            CAN_DATA_TYPE["heart_rate"].dlc,
            CAN_DATA_TYPE["heart_rate"].decimal_digits
        )

        return id, encoded_hr
    

    ###############################################
    ################ DATA DECODING ################
    ###############################################

