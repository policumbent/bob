# from src.mex import Mex
# from src.powermeter import Powermeter
# from src.speed import Speed
# from src.gear import Gear
# from subprocess import call
# from src.settings import Settings
# from src.antSensor import Ant
# import time


# class Raspy:
#     def __init__(self, mex: Mex, speed: Speed, powermeter: Powermeter, gear: Gear, ant=None):
#         self.gear = gear
#         self.speed = speed
#         self.powermeter = powermeter
#         self.mex = mex
#         self.ant = ant

#     @staticmethod
#     def reboot(self):
#         for i in range(0, 10):
#             self.mex.set("Riavvio tra " + str(i + 1) + "secondi", 1, 1)
#             if self.check():
#                 return
#             time.sleep(1)
#         if self.check():
#             call("sudo reboot", shell=True)

#     @staticmethod
#     def poweroff(self):
#         for i in range(0, 10):
#             self.mex.set("Spegnimento tra " + str(i + 1) + "secondi", 1, 1)
#             if self.check():
#                 return
#             time.sleep(1)
#         if self.check():
#             call("sudo poweroff", shell=True)

#     def check(self):
#         speed = self.speed.get()
#         if speed != "-1":
#             if int(speed) > 0:
#                 self.mex.set("Taurus non fermo impossibile spegnere!", 3)
#                 print("Taurus non fermo impossibile spegnere!")
#                 return False

#         gear = self.gear.get()
#         if gear != "0":
#             if gear != str(1):
#                 self.mex.set("E' possibile spegnere Taurus solo in prima marcia!", 3)
#                 print("E' possibile spegnere Taurus solo in prima marcia!")
#                 return False

#         cadence = self.powermeter.getCadence()
#         if cadence != "-1":
#             if int(cadence) > 0:
#                 self.mex.set("Pedali non fermi impossibile spegnere!!", 3)
#                 print("Pedali non fermi impossibile spegnere!!")
#                 return False
#         power = self.powermeter.get()
#         if int(power) > 0:
#             self.mex.set("Potenza rilevata impossibile spegnere!", 3)
#             print("Potenza rilevata impossibile spegnere!")
#             return False
#         return True

#     def closeSoftware(self):
#         # if Settings.monitor:
#         #     monitor.close()
#         # if Settings.video:
#         #     # video.close()
#         for i in range(0, 10):
#             self.mex.set("Riavvio software tra " + str(i + 1) + "secondi", 1, 1)
#             if self.check():
#                 return
#             time.sleep(1)
#         if self.check():
#             if Settings.ant:
#                 self.ant.close()
#             self.powermeter.close()
#             self.speed.close()
#             print("Closing di cattiveria")
#             call("pkill -f python3", shell=True)
