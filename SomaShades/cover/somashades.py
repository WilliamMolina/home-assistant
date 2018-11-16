"""
Simple platform to control Soma Shades
"""

import logging
import json
import voluptuous as vol
import requests
import time
import threading

from homeassistant.const import (ATTR_BATTERY_LEVEL)
from homeassistant.components.cover import (CoverDevice, PLATFORM_SCHEMA, SUPPORT_SET_POSITION, SUPPORT_OPEN, SUPPORT_CLOSE, SUPPORT_STOP, ATTR_POSITION)
from homeassistant.const import (CONF_FRIENDLY_NAME)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_CONTROLLER = 'controller'
CONF_MAC = 'mac'
CONF_COVERS = 'covers'

COVER_SCHEMA = vol.Schema({
    vol.Required(CONF_MAC): cv.string,
    vol.Required(CONF_FRIENDLY_NAME): cv.string
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CONTROLLER): cv.string,
    vol.Required(CONF_COVERS): vol.Schema({cv.slug: COVER_SCHEMA}),
})

API_BASE_URL = None

UPDATE_INTERVAL = 300

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up of the Soma Shades devices."""

    global API_BASE_URL

    API_BASE_URL = "http://" + config.get(CONF_CONTROLLER) + ":8080/"

    # create the update thread
    update_thread = UpdateThread()

    # Get the shades from config
    for device, device_config in config[CONF_COVERS].items():
        friendly_name = device_config.get(CONF_FRIENDLY_NAME, device)
        mac = device_config[CONF_MAC]

        shadeDevice = SomaShadeDevice(device, mac, friendly_name)
        add_devices([shadeDevice])

        # Add it to the update thread
        update_thread.add_device(shadeDevice)

    # Run the update thread
    update_thread.start()

class UpdateThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "SomaShades Update Thread"
        self._devices = []

    def add_device(self, device):
        self._devices.append(device)

    def run(self):
        """
        Runs the update thread
        """

        while(True):
            for device in self._devices:
                device.update_state()

            time.sleep(UPDATE_INTERVAL)

class SomaShadeDevice(CoverDevice):
    
    def __init__(self, entity_id, mac, friendly_name):

        self._mac = mac
        self._friendly_name = friendly_name
        self.entity_id = "cover." + entity_id

        self._position = None
        self._battery_level = 0

        self._failed_updates_counter = 0

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return self._friendly_name

    @property
    def device_class(self):
        return 'window'

    @property
    def unique_id(self):
        return self._mac

    @property
    def available(self):
        return self._position is not None

    @property
    def device_state_attributes(self):
        attr = {
            ATTR_BATTERY_LEVEL: self._battery_level
        }
        return attr

    @property
    def supported_features(self):
        return SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION | SUPPORT_STOP

    @property
    def is_closed(self):
        if self._position is None:
            return None

        return self._position <= 10

    @property
    def current_cover_position(self):
        if self._position is None:
            return None

        # round down
        if self._position <= 5:
            return 0

        # round up
        if self._position >= 95:
            return 100

        return self._position

    def close_cover(self, **kwargs):
        # Move down
        url = API_BASE_URL + "movedown/" + self._mac
        self.SendRequest(url)

        self._position = 0

        # Tell HASS to update
        self.schedule_update_ha_state()

    def open_cover(self, **kwargs):
        # Move up
        url = API_BASE_URL + "moveup/" + self._mac
        self.SendRequest(url)

        self._position = 100

        # Tell HASS to update
        self.schedule_update_ha_state()

    def set_cover_position(self, **kwargs):
        # Set position
        url = API_BASE_URL + "setposition/" + self._mac + "/" + str(kwargs[ATTR_POSITION])
        self.SendRequest(url)
        
        self._position = kwargs[ATTR_POSITION]

        # Tell HASS to update
        self.schedule_update_ha_state()

    def stop_cover(self, **kwargs):
        # Stop
        url = API_BASE_URL + "stop/" + self._mac
        self.SendRequest(url)

    #def update(self):
    #    """Retrieve latest state. Not needed since updates are handled asynchronously"""
    #   return True

    def update_state(self):
        
        get_position_url = API_BASE_URL + "getposition/" + self._mac 
        get_battery_url = API_BASE_URL + "getbattery/" + self._mac

        try:
            resp = self.SendRequest(get_position_url)
            self._position = int(resp.text)

            resp = self.SendRequest(get_battery_url)
            self._battery_level = int(resp.text)

            _LOGGER.debug("{}: Position={}, battery level={}".format(self._friendly_name, self._position, self._battery_level))

            self._failed_updates_counter = 0

            # Tell HASS to update
            self.schedule_update_ha_state()

        except Exception as err:
            self._failed_updates_counter += 1
            # Log an error if we failed 3 times in a row, otherwise log a warning
            if self._failed_updates_counter == 3:
                _LOGGER.error("{}: Multiple updates failed - error ({})".format(self._friendly_name, err))
            else:
                _LOGGER.warning("{}: Update error ({})".format(self._friendly_name, err))

    def SendRequest(self, url):

        _LOGGER.debug("{}: Sending GET to {}".format(self._friendly_name, url))
        resp = requests.get(url, timeout=10)

        if resp.status_code != 200:
            # Something went wrong, try again
            _LOGGER.warning('{}: GET {} failed with status {}, retrying'.format(self._friendly_name, url, resp.status_code))
            resp = requests.get(url, timeout=10)

        if resp.status_code != 200:
            _LOGGER.error('{}: GET {} failed with status {}'.format(self._friendly_name, url, resp.status_code))

        return resp