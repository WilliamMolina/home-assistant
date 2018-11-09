"""
Simple platform to control Moodo Aroma Diffuser devices (exposed as lights to enable fan speed control via brightness)
"""

import logging
import json
import voluptuous as vol
import requests
import time

from homeassistant.components.light import (Light, PLATFORM_SCHEMA, ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS)
from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_ID, CONF_SWITCHES, CONF_FRIENDLY_NAME)
from homeassistant.helpers.service import extract_entity_ids
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_API_TOKEN = 'api_token'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_TOKEN): cv.string,
})

API_BASE_URL = "https://rest.moodo.co/api/boxes"
API_TOKEN = None
HEADERS = None

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up of the Moodo devices."""

    global HEADERS

    API_TOKEN = config.get(CONF_API_TOKEN)
    HEADERS = {"token": API_TOKEN, "accept":"application/json"}

    # Get the Moodo boxes
    _LOGGER.debug("Sending GET to {} with headers={}".format(API_BASE_URL, HEADERS))
    resp = requests.get(API_BASE_URL, headers=HEADERS)
    if resp.status_code != 200:
        # Something went wrong
        raise Exception('GET {} failed with status {}, error: {}'.format(API_BASE_URL, resp.status_code, resp.json()["error"]))

    # Enumerate Moodo boxes and create a device for each one
    for moodo_json in resp.json()['boxes']:
        moodo = MoodoDevice(moodo_json['device_key'], moodo_json['id'], moodo_json['name'])
        add_devices([moodo])

class MoodoDevice(Light):
    
    def __init__(self, device_key, device_id, device_name):

        self._device_key = device_key
        self._device_id = device_id
        self._device_name = device_name + " Aroma Diffuser"

        self._API_BOX_URL = API_BASE_URL + "/" + str(self._device_key)

        _LOGGER.info('Setting up {}, device_key={}'.format(self._device_name, self._device_key))

        self._data = {}
        self._available = False
        self._state = False
        self._fan_volume = 0

    @property
    def should_poll(self):
        return True

    @property
    def name(self):
        return self._device_name

    @property
    def unique_id(self):
        return self._device_id

    @property
    def available(self):
        return self._available

    @property
    def is_on(self):
        return self._state

    @property
    def device_state_attributes(self):
        return self._data

    @property
    def brightness(self):
        # Return fan volume as brightness
        return self._fan_volume

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS

    def set_state(self, state, fan_volume):

        fan_speed = 0
        if state == True:
            fan_speed = 25

        # Turn ON or OFF
        json = {
                    "device_key": self._device_key,
                    "fan_volume": fan_volume * 100 / 255,           # Limit to 0..100
                    "box_status": 1,
                    "settings_slot0":
                    {
                        "fan_speed": fan_speed,
                        "fan_active": state
                    },
                    "settings_slot1":
                    {
                        "fan_speed": fan_speed,
                        "fan_active": state
                    },
                    "settings_slot2":
                    {
                        "fan_speed": fan_speed,
                        "fan_active": state
                    },
                    "settings_slot3":
                    {
                        "fan_speed": fan_speed,
                        "fan_active": state
                    }
                }

        _LOGGER.debug("Sending POST to {} with headers={} json={}".format(API_BASE_URL, HEADERS, json))
        resp = requests.post(API_BASE_URL, json=json, headers=HEADERS)
        if resp.status_code != 200:
            # Something went wrong
            raise Exception('POST {} (payload={}) for {} failed with status {}, error {}'.format(API_BASE_URL, json, self._device_name, resp.status_code, resp.json()))

        self._fan_volume = fan_volume
        self._state = state

    def turn_on(self, **kwargs):

        fan_volume = self._fan_volume
        if ATTR_BRIGHTNESS in kwargs:
            fan_volume = kwargs[ATTR_BRIGHTNESS]

        self.set_state(True, fan_volume)

    def turn_off(self, **kwargs):
        self.set_state(False, self._fan_volume)

    def update(self):
        
        # Retry 3 times
        MAX_RETRIES = 3
        for x in range(MAX_RETRIES):
            resp = None
            try:
                _LOGGER.debug("Sending GET to {} with headers={}".format(self._API_BOX_URL, HEADERS))
                resp = requests.get(self._API_BOX_URL, headers=HEADERS)
                if resp.status_code != 200:
                    # Something went wrong
                    raise Exception('GET {} failed with status {}, error: {}'.format(self._API_BOX_URL, resp.status_code, resp.json()["error"]))

                break
            except Exception as err:
                if x == (MAX_RETRIES - 1):
                    _LOGGER.error('GET {} failed with exception {}'.format(self._API_BOX_URL, err))
                    return      # Just return out, state will be left as what it was previously

                _LOGGER.warning('GET {} failed with exception {}. Will retry'.format(self._API_BOX_URL, err))

        self._data = resp.json()
        self._available = self._data["box"]["is_online"]

        # We consider the Moodo to be on if any fan is active
        # Note, box.box_status reports 1 even if no fans are active (i.e. Moodo treats this case as 'on' state but we don't)
        self._state = False
        if self._data["box"]["box_status"] == 1:
            for settings in self._data["box"]["settings"]:
                if settings["fan_active"] == True:
                    self._state = True
                    break

        self._fan_volume = self._data["box"]["fan_volume"] * 255 / 100      # 0..255
