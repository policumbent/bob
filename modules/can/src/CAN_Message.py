from CAN_ID import *
from CAN_DataType import CAN_DATA_TYPE

class CAN_Message:
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

    
    def enc_speed(self, speed):
        """
        encodes speed in ByteArray format
        :param speed
        :return id -> int, encoded_speed -> ByteArray
        """

        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HS_SPEED)

        encoded_speed = self._encode_data(
            speed,
            CAN_DATA_TYPE["speed"].dlc,
            CAN_DATA_TYPE["speed"].decimal_digits
        )

        return id, encoded_speed
    

    def enc_distance(self, distance):
        """
        encodes distance in ByteArray format
        :param distance
        :return id -> int, encoded_distance -> ByteArray
        """
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HS_DISTANCE)

        encoded_distance = self._encode_data(
            distance,
            CAN_DATA_TYPE["distance"].dlc,
            CAN_DATA_TYPE["distance"].decimal_digits
        )

        return id, encoded_distance


    def enc_wheel_rpm(self, rpm):
        """
        encodes rpm in ByteArray format
        :param rpm
        :return id -> int, encoded_rpm -> ByteArray
        """

        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HS_W_RPM)

        encoded_rpm = self._encode_data(
            rpm,
            CAN_DATA_TYPE["rpm"].dlc,
            CAN_DATA_TYPE["rpm"].decimal_digits    
        )

        return id, encoded_rpm


    def enc_pedal_rpm(self, rpm):
        """
        encodes rpm in ByteArray format
        :param rpm
        :return id -> int, encoded_rpm -> ByteArray
        """

        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_SRM_P_RPM)

        encoded_rpm = self._encode_data(
            rpm,
            CAN_DATA_TYPE["rpm"].dlc,
            CAN_DATA_TYPE["rpm"].decimal_digits
        )

        return id, encoded_rpm

    
    def enc_power(self, power):
        """
        encodes power in ByteArray format
        :param power
        :return id -> int, encoded_power -> ByteArray
        """
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_SRM_PWR)

        encoded_power = self._encode_data(
            power,
            CAN_DATA_TYPE["power"].dlc,
            CAN_DATA_TYPE["power"].decimal_digits
        )

        return id, encoded_power


    def enc_heartrate(self, heart_rate):
        """
        encodes heart_rate in ByteArray format
        :param heart_rate
        :return id -> int, encoded_hr -> ByteArray
        """

        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HEART_RATE)

        encoded_hr = self._encode_data(
            heart_rate,
            CAN_DATA_TYPE["heart_rate"].dlc,
            CAN_DATA_TYPE["heart_rate"].decimal_digits
        )

        return id, encoded_hr