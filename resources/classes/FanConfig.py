from resources.lib.helpers import is_integer, parse_multi_dim_sequence_str, \
	string_is_empty, check_int_ranges, are_integerishs
import xbmcaddon
import xbmc
from resources.lib.kodiutils import showmessage


class FanConfig:
	gpio = None
	freq = None
	interval = None
	fanstartlevel = None
	constant_speed = None
	temp_thresholds = None
	variable_speeds = None
	fan_cooldown_interval = None
	fan_cooldown_time = None
	variable_fan_speeds = None
	use_variable_speed = False

	def __init__(self, addon, logger):
		# type: (xbmcaddon.Addon) -> None
		prefix = "buccaneersdan.pyfoehn."
		pwmgpio = addon.getSetting(prefix + "pwmgpio")
		freq = addon.getSetting(prefix + "freq")
		interval = addon.getSetting(prefix + "interval")
		fanstartlevel = addon.getSetting(prefix + "fanstartlevel")
		constant_speed = addon.getSetting(prefix + "constant_speed")
		fancooldown = addon.getSetting(prefix + "fancooldown")

		self.use_variable_speed = addon.getSetting(prefix + "variable_speed")

		if not string_is_empty(fancooldown):
			pos_sec = fancooldown.find("sec")
			pos_min = fancooldown.find("min")
			pos_hrs = fancooldown.find("hrs")
			if pos_sec > -1:
				self.fan_cooldown_time = int(fancooldown[0:pos_sec])
			elif pos_min > -1:
				self.fan_cooldown_time = int(fancooldown[0:pos_min]) * 60
			elif pos_hrs > -1:
				self.fan_cooldown_time = int(fancooldown[0:pos_hrs]) * 3600
			else:
				self.fan_cooldown_interval = int(fancooldown)
		elif is_integer(fancooldown):
			self.fan_cooldown_interval = fancooldown
		else:
			self.fan_cooldown_time = 10

		optionnames = [
			"PWM-GPIO-Port", "Frequency",
			"Interval", "Fan-Start-Level",
			"Constant-Speed"
		]

		ranges = addon.getSetting(prefix + "rangevalues")

		if not string_is_empty(ranges):
			ranges = parse_multi_dim_sequence_str(ranges, lambda x: [int(a) for a in x])
		else:
			ranges = [[2, 27], [0, 500], [5, 30], [1, 4], [0, 100]]

		# xbmc.log("{},{},{},{}".format(freq, interval, fanstartlevel, constant_speed))
		# xbmc.log(str(ranges))

		check = check_int_ranges(
			[pwmgpio, freq, interval, fanstartlevel, constant_speed],
			ranges,
		)

		if check is not None:
			raise Exception("Supply a number between {} and {} for settings-value {}".format(
				ranges[check][0],
				ranges[check][1],
				optionnames[check]
			))

		tt1 = addon.getSetting(prefix + "temperature_threshold_1")
		tt2 = addon.getSetting(prefix + "temperature_threshold_2")
		tt3 = addon.getSetting(prefix + "temperature_threshold_3")
		tt4 = addon.getSetting(prefix + "temperature_threshold_4")
		tt5 = addon.getSetting(prefix + "temperature_threshold_5")
		intcheck = are_integerishs(tt1, tt2, tt3, tt4, tt5)
		if intcheck is False:
			raise Exception("One temperature_threshold settings is incorrect")
		self.temp_thresholds = [int(tt1), int(tt2), int(tt3), int(tt4), int(tt5)]

		if self.use_variable_speed is True:
			vs1 = addon.getSetting(prefix + "variable_fan_speed_1")
			vs2 = addon.getSetting(prefix + "variable_fan_speed_2")
			vs3 = addon.getSetting(prefix + "variable_fan_speed_3")
			vs4 = addon.getSetting(prefix + "variable_fan_speed_4")
			vs5 = addon.getSetting(prefix + "variable_fan_speed_5")
			intcheck = are_integerishs(vs1, vs2, vs3, vs4, vs5)
			if intcheck is False:
				raise Exception("One variable_fan_speed settings is incorrect")

			self.variable_fan_speeds = [int(vs1), int(vs2), int(vs3), int(vs4), int(vs5)]

		self.gpio = int(pwmgpio)
		self.freq = int(freq)
		self.interval = int(interval)
		self.fanstartlevel = int(fanstartlevel)
		self.constant_speed = int(constant_speed)