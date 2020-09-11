from time import sleep
from resources.classes.FanConfig import FanConfig
from logging import Logger
import sys

sys.path.append("/storage/.kodi/addons/virtual.rpi-tools/lib")
import RPi.GPIO as GPIO


class FanHandler:
	fanconfig = None
	""":type: FanConfig"""

	logger = None
	""":type: Logger"""

	fanstarted = False
	""":type: bool"""

	fan = None

	destroyed = True
	""":type: bool"""

	current_dutycycle = None
	""":type: int"""

	def __init__(self, fanconfig, logger):
		self.fanconfig = fanconfig
		self.logger = logger
		self.dbgwrite("Setting up GPIO")
		self.dbgwrite("gpioport={}, frequency={}".format(self.fanconfig.gpio, self.fanconfig.freq))
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.fanconfig.gpio, GPIO.OUT)
		self.fan = GPIO.PWM(self.fanconfig.gpio, self.fanconfig.freq)
		self.destroyed = False

	def dbgwrite(self, msg, *args, **kwargs):
		self.logger.debug(msg, *args, **kwargs)

	def startfan(self, default_dutycycle=0):
		self.fan.start(default_dutycycle)
		self.current_dutycycle = default_dutycycle
		self.dbgwrite("Started PWM with dutycycle {}".format(default_dutycycle))
		self.fanstarted = True

	def setdutycycle(self, dutycycle):
		self.dbgwrite("Changed dutycycle to {}".format(dutycycle))
		self.current_dutycycle = dutycycle
		self.fan.ChangeDutyCycle(dutycycle)

	def stopfan(self):
		self.fan.stop()
		self.fanstarted = False

	def destroy(self):
		self.dbgwrite("Stopping Fan")
		self.fan.stop()
		self.dbgwrite("GPIO Cleanup")
		GPIO.cleanup()
		self.destroyed = True
#