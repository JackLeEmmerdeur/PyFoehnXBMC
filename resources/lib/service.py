# -*- coding: utf-8 -*-

# from resources.lib import kodiutils
# from resources.lib import kodilogging
# import logging
# import time
# import xbmcgui
# from resources.lib.helpers import get_reformatted_exception
# from resources.lib.helpers import string_is_empty, check_int_ranges, are_integerishs, parse_multi_dim_sequence_str
# from resources.lib.kodiutils import showmessage

import xbmc
import xbmcaddon
from logging import Logger
from resources.classes.FanConfig import FanConfig
from resources.classes.FanHandler import FanHandler
from resources.lib.helpers import get_soctemp
from time import time


def setfandutycycle(logger, fan, olddutycycle, newdutycycle):
	if olddutycycle != newdutycycle:
		logger.debug("Set dutycycle {}".format(newdutycycle))
		fan.setdutycycle(newdutycycle)
		return newdutycycle
	return olddutycycle


def run(addon, logger):
	# type: (xbmcaddon.Addon, Logger) -> None

	fanconfig = FanConfig(addon, logger)
	fan = FanHandler(fanconfig, logger)
	fan.startfan(0)
	fan_started = False
	fan_olddutycycle = 0
	fan_started_cooldown = False
	fan_cooldown_intervals_ticked = None
	fan_cooldown_time_started = None

	monitor = xbmc.Monitor()

	while not monitor.abortRequested():

		try:
			soctemp = get_soctemp(True)

			if soctemp < fanconfig.temp_thresholds[0]:
				# Temperature fell below the first
				# temperature-control-point, which
				# probably means that the socket
				# doesn't need cooling so stop the fan
				logger.debug("Temperature below cool")
				if fan_started is True:
					fan_olddutycycle = setfandutycycle(logger, fan, fan_olddutycycle, 0)
					fan_started = False
			elif fan_started is True:
				# Fan is already running
				if fan_started_cooldown is False and \
						soctemp < fanconfig.temp_thresholds[fanconfig.fanstartlevel-1]:

					# We're not in the cooldown phase (CP),
					# but socket temperature has normalized,
					# so start CP

					fan_started_cooldown = True

					logger.debug("Back at defcon 0")

					if fanconfig.fan_cooldown_interval is not None:
						# CP will use interval-mode
						fan_cooldown_intervals_ticked = 0
					else:
						# CP will use time-period-mode
						fan_cooldown_time_started = time()

				if fan_started_cooldown is True:
					# CP was started so check its stop-condition
					if fanconfig.fan_cooldown_interval is not None:
						# ---------- CP-Interval-Mode
						logger.debug("Current interval-cooldown-ticker={}".format(
							fan_cooldown_intervals_ticked)
						)
						# Check stop-condition:
						# Ticks of check-interval reached max interval config-value
						if fan_cooldown_intervals_ticked == fanconfig.fan_cooldown_interval:
							# The interval-cooldown-ticker is zero...
							if soctemp < fanconfig.temp_thresholds[fanconfig.fanstartlevel-1]:
								# Stop fan because current temperature is
								# below the fan-startlevel-temperature again

								fan_olddutycycle = setfandutycycle(logger, fan, fan_olddutycycle, 0)
								fan_started = False
								fan_started_cooldown = False

							# Reset CP-cooldown-ticker. So either
							# the fan was stopped above or it runs for
							# another CP-cooldown-ticker round
							fan_cooldown_intervals_ticked = 0
						else:
							# Advance the CP-interval
							fan_cooldown_intervals_ticked += 1
					else:
						# ---------- CP-Cooldown-Mode is used

						current_time = time()
						seconds_passed = int(current_time - fan_cooldown_time_started)
						logger.debug("Current timer-cooldown seconds passed={}".format(
							seconds_passed
						))

						if seconds_passed >= fanconfig.fan_cooldown_time:
							# Fan-cooldown-time has elapsed

							if soctemp < fanconfig.temp_thresholds[fanconfig.fanstartlevel-1]:
								# Stop fan because current temperature is
								# below the fan-startlevel-temperature again
								fan_olddutycycle = setfandutycycle(logger, fan, fan_olddutycycle, 0)
								fan_started = False
								fan_started_cooldown = False

							# Reset cooldown-timer. So either the fan
							# was stopped above or it runs for another
							# cooldown-timer-round
							fan_cooldown_time_started = current_time

			else:
				# Fan isn't running so determine if the
				# socket temperature reached one of the
				# temperature-control-points
				for index, temp in enumerate(fanconfig.temp_thresholds):
					if soctemp >= temp:
						if index+1 >= fanconfig.fanstartlevel:
							# The fan should be started if the
							# socket-temperature exeeds the
							# temperature-control-point
							logger.debug("Fan start level {} reached({}deg)".format(
								fanconfig.fanstartlevel,
								temp
							))
							dtindex = index

							if fanconfig.use_variable_speed is True:
								# Set the speed to the corresponding
								# variable-fan-speed of the current
								# temperature-control-point
								speed = fanconfig.variable_fan_speeds[dtindex]
							elif fanconfig.constant_speed > 0:
								# Set the fan-speed to constant
								speed = fanconfig.constant_speed
							else:
								# Set speed to the corresponding
								# procentual value of the
								# temperature-control-point
								speed = ((dtindex + 1) * 100) / float(len(fanconfig.temp_thresholds))

							fan_olddutycycle = setfandutycycle(logger, fan, fan_olddutycycle, speed)
							fan_started = True
		except:
			import traceback
			logger.debug(traceback.format_exc())
			break

		# Sleep/wait for abort for 10 seconds
		if monitor.waitForAbort(fan.fanconfig.interval):
			# Abort was requested while waiting. We should exit
			break

	fan.stopfan()
	fan.destroy()