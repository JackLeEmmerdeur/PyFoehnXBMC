# -*- coding: utf-8 -*-

from resources.lib import kodilogging, service
import logging
import xbmcaddon
import xbmc

addon = xbmcaddon.Addon()
xbmc.log(addon.getAddonInfo('id'))
kodilogging.config()
logger = logging.getLogger(addon.getAddonInfo('id'))
service.run(addon, logger)
