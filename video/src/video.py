import picamera  # pylint: disable=import-error
import threading
import os

from time import sleep
from PIL import Image, ImageDraw, ImageFont
from .bikeData import BikeData
from .settings import Settings

FONT = "resources/FreeSans.ttf"


class Video:

    def __init__(self, bike_data: BikeData, settings: Settings):
        print("Starting video")
        self._video_name = "video_record"
        self._state = False
        self._bike_data = bike_data
        self._settings = settings

        self._p13 = False

        self.recording_started = False
        # if not local.get("video", True):
        #     return
        # self._worker = threading.Thread(target=self._run, daemon=False)
        # self._worker.start()
        self._run()

    @classmethod
    def _print(cls, name, value, unit):
        return f'{name} {value} {unit}' if value != "" else ''

    def start_recording(self, value):
        pass
        # self._video_record = value

    def _run(self):
        print("Starting video")

        # Video Resolution
        video_height = 480
        video_width = 800

        # telemetry_icon = Image.open('src/icons/icona_telemetria.png')
        # record_video_icon = Image.open('src/icons/icona_video.png')
        # USATO PRINCIPALMENTE PER TESTARE LA TELEMETRIA, MA POTREMMO TENERE LA SORPRESA PER ANDREA, TENETELO SEGRETO
        # if int(self.settings.get("bike")) == 0:
        #     img_p13 = Image.open('src/icons/antilope.png')
        # else:
        #     img_p13 = Image.open('src/icons/minions.png')

        frame = Image.new("RGBA", (video_width, video_height))

        # framePixels = frame.load()
        frame.load()
        with picamera.PiCamera() as camera:
            camera.resolution = (video_width, video_height)
            camera.framerate = 90
            camera.rotation = 180
            # MASSIMO 57 POI DEGRADA LE  IMMAGINI (FORSE E' LA CAMERA VECCHIA)
            camera.framerate = 55
            # camera.led = False
            # camera.expsure_speed = 100
            # TODO: da testare la stabilizzazione
            camera.video_stabilization = True
            camera.start_preview()
            img = frame.copy()

            overlay = camera.add_overlay(img.tobytes(), layer=3, alpha=100)
            sleep(0.25)

            # TODO: capire a cosa serve questo try
            #try:
                while True:
                    # REGISTRAZIONE SCHERMO
                    if self._settings.video_record:
                        # TODO: dovremmo fare un check dello spazio di archiviazione disponibile
                        if not self.recording_started:
                            dir_video = 'video'
                            if dir_video not in os.listdir(self._settings.usb_path):
                                os.mkdir(self._settings.usb_path + dir_video)

                            data = self._bike_data
                            time_t = str(data.timestamp)
                            time_t = time_t.replace("/", ".")
                            time_t = time_t.replace(" ", "_")
                            camera.start_recording(self._settings.usb_path + dir_video + "/" + self.video_name + "-"
                                                   + time_t + '.h264')

                            self.recording_started = True
                        camera.annotate_foreground = picamera.Color('black')
                        camera.annotate_text = self._print('Speed: ', self._bike_data.speed, ' km/h')
                    else:
                        if self.recording_started:
                            camera.stop_recording()
                            # self._mex.set("Registrazione video fermata", 3)
                            self.recording_started = False
                            camera.annotate_text = ""
            # try:
            while True:
                # REGISTRAZIONE SCHERMO
                # if self._video_record:
                #     # TODO: dovremmo fare un check dello spazio di archiviazione disponibile
                #     if not self.recording_started:
                #         dir_video = 'video'
                #         if dir_video not in os.listdir(self._settings.USB_PATH):
                #             os.mkdir(self._settings.USB_PATH + dir_video)
                #
                #         data = self._bike_data
                #         time_t = str(data.timestamp)
                #         time_t = time_t.replace("/", ".")
                #         time_t = time_t.replace(" ", "_")
                #         camera.start_recording(self._settings.USB_PATH + dir_video + "/" + self.video_name + "-"
                #                                + time_t + '.h264')
                #
                #         self.recording_started = True
                #     camera.annotate_foreground = picamera.Color('black')
                #     camera.annotate_text = self._print('Speed: ', self._bike_data.speed, ' km/h')
                # else:
                #     if self.recording_started:
                #         camera.stop_recording()
                #         # self._mex.set("Registrazione video fermata", 3)
                #         self.recording_started = False
                #         camera.annotate_text = ""

                # I valori sono mostrati a schermo
                # su due righe parallele
                # TODO: METTERE LOCK
                data = self._bike_data

                print_data = self._print
                bike = data.bikeName
                hr = print_data('FC: ', data.heartrate, 'bpm')

                speed = print_data('Vel:', data.speed, 'km/h')
                distance = print_data('Dist:', data.distance, 'km')
                cadence = print_data('Cad:', data.cadence, 'rpm')
                power = print_data('Power:', data.power, 'W')
                gear = print_data('M:', data.gear, '')
                timer = print_data('Timer: ', data.timeStr, '')
                trap_info = ""
                mex = data.line1
                mex2 = data.line2

                # img = frame.copy()
                # if self._video_record:
                #     img.paste(record_video_icon, (300, 10))
                # if self.settings.get("telemetry_connected"):
                #     img.paste(telemetry_icon, (420, 10))
                # # USATO PRINCIPALMENTE PER TESTARE LA TELEMETRIA,
                # # MA POTREMMO TENERE LA SORPRESA PER ANDREA, TENETELO SEGRETO
                # if self._p13:
                #     if speed == 0:
                #         img.paste(img_p13, (100, 60), img_p13)
                #
                draw = ImageDraw.Draw(img)
                draw.font = ImageFont.truetype(FONT, 40)

                color = tuple(self._settings.default_color_1)
                color2 = tuple(self._settings.default_color_2)
                print(color)
                print(color2)
                if bike == 'taurus':
                    draw.text((10, 40), hr, color2)
                    draw.text((540, 5), distance, color2)
                    draw.text((10, 5), timer, color2)
                    draw.text((540, 40), cadence, color2)
                elif bike == 'taurusx':
                    draw.text((540, 5), cadence, color2)
                draw.text((10, 430), speed, color)
                draw.text((360, 430), gear, color)
                draw.text((540, 430), power, color)

                    if self._settings.power_speed_simulator:
                        self.show_estimator(draw)

                # draw.text((10, 5), hr, (255, 255, 255))
                # draw.text((530, 5), speed, (255, 255, 255))
                # draw.text((530, 40), distance, (255, 255, 255))
                # draw.text((10, 430), cadence, (255, 255, 255))
                # draw.text((10, 395), timer, (255, 255, 255))
                # draw.text((540, 430), power, (255, 255, 255))
                # draw.text((360, 430), gear, (255, 255, 255))

                x1 = int((800 - 20 * (mex.__len__())) / 2)
                x2 = int((800 - 20 * (mex2.__len__())) / 2)
                x3 = int((800 - 18 * (trap_info.__len__())) / 2)
                draw.text((x1, 80), mex, color2)
                draw.text((x2, 115), mex2, color2)
                draw.text((x3, 150), trap_info, color2)

                overlay.update(img.tobytes())
                sleep(0.25)
            # except Exception as e:
            #     print(e)

            # finally:
            #     camera.remove_overlay(overlay)

    @property
    def video_name(self):
        return self._video_name

    @video_name.setter
    def video_name(self, value: str):
        # TODO: implementare lock
        self._video_name = value

    def show_estimator(self, draw):
        if self._bike_data.targetSpeed == 0:
            return
        target_power = self._bike_data.targetPower
        target_speed = self._bike_data.targetSpeed

        current_power = self._bike_data.power
        current_speed = self._bike_data.speed

        diff_power = int(current_power) - target_power
        diff_speed = round(float(current_speed) - target_speed, 1)

        if diff_speed >= 5:
            arrow = "↗"
            color = (0, 255, 0)
            text = "+" + str(diff_speed)
        elif diff_speed <= -5:
            arrow = "↘"
            color = (255, 0, 0)
            text = str(diff_speed)
        else:
            arrow = "→"
            color = self._settings.default_color_1
            text = str(diff_speed)

        # DISEGNO LA FRECCIA
        draw.text((30, 395), arrow, color)

        # SCRIVO LA DIFFERENZA DI VELOCITA'
        draw.text((90, 395), text + " km/h", color)

        if diff_power >= 10:
            color = (0, 255, 0)
            arrow = "↗"
            text = "+" + str(diff_power)
        elif diff_power <= -10:
            color = (255, 0, 0)
            arrow = "↘"
            text = str(diff_power)
        else:
            color = self._settings.default_color_1
            arrow = "→"
            text = str(diff_power)

        # SCRIVO LA DIFFERENZA DI POTENZA
        draw.text((680, 395), text + " W", color)
        draw.text((620, 395), arrow, color)

