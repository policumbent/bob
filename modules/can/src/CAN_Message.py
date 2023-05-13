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

class CAN_Message:
    def rounder(self, data, decimal_digits):
        """
        rounding data function
        :param data: data to be rounded
        :param decimal_digits: number of input decimal digits
        :return rounded data, formatted as int
        """
        return int(round(data, decimal_digits)) * pow(10, decimal_digits)
    
    def enc_speed(self, speed):
        """
        encoding speed function
        :param speed taken from MQTT server
        :return id, bytearray:encoded_speed
        """

        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HS_SPEED)
        rounded_speed = self.rounder(speed, 2)

        encoded_speed = bytearray([
            rounded_speed & 0xff00,
            rounded_speed & 0x00ff
        ])

        return id, encoded_speed
    

    def enc_distance(self, distance):
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HS_DISTANCE)
        rounded_dist = self.rounder(distance, 0)

        encoded_distance = bytearray([
            rounded_dist & 0xff00,
            rounded_dist & 0x00ff
        ])

        return id, encoded_distance


    def enc_wheel_rpm(self, rpm):
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HS_W_RPM)
        rounded_rpm = self.rounder(rpm, 1)

        encoded_rpm = bytearray([
            rounded_rpm & 0xff00,
            rounded_rpm & 0x00ff
        ])

        return id, encoded_rpm


    def enc_pedal_rpm(self, rpm):
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_SRM_P_RPM)
        rounded_rpm = self.rounder(rpm, 1)

        encoded_rpm = bytearray([
            rounded_rpm & 0xff00,
            rounded_rpm & 0x00ff
        ])

        return id, encoded_rpm

    
    def enc_power(self, power):
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_SRM_PWR)
        rounded_power = self.rounder(power, 1)

        encoded_power = bytearray([
            rounded_power & 0xff00,
            rounded_power & 0x00ff
        ])

        return id, encoded_power


    def enc_heartrate(self, heartrate):
        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HEART_RATE)
        rounded_hr = self.rounder(heartrate, 0)

        encoded_hr = bytearray([
            rounded_hr & 0xff
        ])

        return id, encoded_hr