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
    def rounder(self, data_to_round, digits):
        '''
       function to round data to dedired float with n digits then multiplied by the same amount of 10*n to render it an int.'''
        return int(round(data_to_round, digits))*10^digits
    
    def enc_speed(self, speed):
        """encoding speed function
        :param speed taken from MQTT server
        :return id, bytearray:encoded_speed"""

        id = (MSG_DATA << 9) | (DEV_RPI_DATA << 5) | (RPI_HS_SPEED)
        rounded_speed = self.rounder(speed, 2)

        encoded_speed = bytearray([
            rounded_speed & 0xff00,
            rounded_speed & 0x00ff
        ])

        return id, encoded_speed
    

    def enc_distance(self, distance):
        rounded_dist = self.rounder(distance, 0)

        encoded_distance = bytearray([
            rounded_dist & 0xff00,
            rounded_dist & 0x00ff
        ])

        return id, encoded_distance


    def enc_rpm(self, rpm):
        pass

    
    def enc_power(self, power):
        pass


    def enc_heartrate(self, heartrate):
        pass