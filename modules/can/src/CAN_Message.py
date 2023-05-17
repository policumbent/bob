ID_TYPE_MASK    = 0b11000000000  # not used
ID_DEV_MASK     = 0b00111100000
ID_SPEC_MASK    = 0b00000011111

MSG_DEBUG       = 0
MSG_ERROR       = 1
MSG_DATA        = 2
MSG_INFO        = 3

DEV_CORE_RPI    = 0b0000
DEV_GEARBOX     = 0b0001
DEV_RPI_DATA    = 0b0010
DEV_GSM_DATA    = 0b0100
DEV_LOW_PRTY    = 0b1000

GB_LMT_SWITCH   = 0b00000
GB_RECEIVER     = 0b00001   # Cerberus only
GB_GEARBOX      = 0b00010

RPI_HS_SPEED    = 0b00000
RPI_HS_DISTANCE = 0b00001
RPI_HS_W_RPM    = 0b00010
RPI_SRM_PWR     = 0b00100
RPI_SRM_P_RPM   = 0b00101
RPI_HEART_RATE  = 0b01100

GSM_GPS_SPEED   = 0b00000
GSM_GPS_DIST    = 0b00001
# GSM_GPS_COOR     0b00010

DT_ERROR        = 1
DT_SPEED        = 2
DT_DISTANCE     = 3
DT_RPM          = 4
DT_POWER        = 5
DT_HEARTRATE    = 6
DT_GEAR         = 7

from CAN_DataType import CAN_DATA_TYPE

class CAN_Message:
    def encode_data(self, data, dlc, decimal_digits):
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
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HS_SPEED)

        encoded_speed = self.encode_data(
            speed,
            CAN_DATA_TYPE["speed"].dlc,
            CAN_DATA_TYPE["speed"].decimal_digits
        )

        return id, encoded_speed
    

    def enc_distance(self, distance):
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HS_DISTANCE)

        encoded_distance = self.encode_data(
            distance,
            CAN_DATA_TYPE["distance"].dlc,
            CAN_DATA_TYPE["distance"].decimal_digits
        )

        return id, encoded_distance


    def enc_wheel_rpm(self, rpm):
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HS_W_RPM)

        encoded_rpm = self.encode_data(
            rpm,
            CAN_DATA_TYPE["rpm"].dlc,
            CAN_DATA_TYPE["rpm"].decimal_digits    
        )

        return id, encoded_rpm


    def enc_pedal_rpm(self, rpm):
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_SRM_P_RPM)

        encoded_rpm = self.encode_data(
            rpm,
            CAN_DATA_TYPE["rpm"].dlc,
            CAN_DATA_TYPE["rpm"].decimal_digits
        )

        return id, encoded_rpm

    
    def enc_power(self, power):
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_SRM_PWR)

        encoded_power = self.encode_data(
            power,
            CAN_DATA_TYPE["power"].dlc,
            CAN_DATA_TYPE["power"].decimal_digits
        )

        return id, encoded_power


    def enc_heartrate(self, heartrate):
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HEART_RATE)

        encoded_hr = self.encode_data(
            heartrate,
            CAN_DATA_TYPE["heart_rate"].dlc,
            CAN_DATA_TYPE["heart_rate"].decimal_digits
        )

        return id, encoded_hr