"""Platform for Crestron Media Player integration."""
"""Modified for use for Crestron AADS"""

import voluptuous as vol
import logging
import asyncio

import homeassistant.helpers.config_validation as cv
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_STEP,
)
from homeassistant.const import STATE_ON, STATE_OFF, CONF_NAME
from .const import (
    HUB,
    DOMAIN,
    CONF_MUTE_JOIN,
    CONF_VOLUME_JOIN,
    CONF_VOLUME_UP_JOIN,
    CONF_VOLUME_DOWN_JOIN,
    CONF_OFF_JOIN,
    CONF_SOURCE_NUM_JOIN
)

_LOGGER = logging.getLogger(__name__)

SOURCES_SCHEMA = vol.Schema (
    {
        cv.positive_int: cv.string,
    }
)

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_MUTE_JOIN): cv.positive_int,           
        vol.Required(CONF_SOURCE_NUM_JOIN): cv.positive_int,           
        vol.Required(CONF_VOLUME_UP_JOIN): cv.positive_int,
        vol.Required(CONF_VOLUME_DOWN_JOIN): cv.positive_int,
        vol.Required(CONF_OFF_JOIN): cv.positive_int,
        vol.Required(CONF_VOLUME_JOIN): cv.positive_int
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN][HUB]
    entity = [CrestronRoom(hub, config)]
    async_add_entities(entity)


class CrestronRoom(MediaPlayerEntity):
    def __init__(self, hub, config):
        self._hub = hub
        self._name = config.get(CONF_NAME)
        self._device_class = "speaker"
        self._supported_features = (
            SUPPORT_VOLUME_MUTE
            | SUPPORT_VOLUME_STEP
            | SUPPORT_TURN_OFF
            | SUPPORT_TURN_ON
        )
        self._mute_join = config.get(CONF_MUTE_JOIN)
        self._volume_up_join = config.get(CONF_VOLUME_UP_JOIN)
        self._volume_down_join = config.get(CONF_VOLUME_DOWN_JOIN)
        self._volume_level_join = config.get(CONF_VOLUME_JOIN)
        self._source_number_join = config.get(CONF_SOURCE_NUM_JOIN)
        self._off_join = config.get(CONF_OFF_JOIN)

    async def async_added_to_hass(self):
        self._hub.register_callback(self.process_callback)

    async def async_will_remove_from_hass(self):
        self._hub.remove_callback(self.process_callback)

    async def process_callback(self, cbtype, value):
        self.async_write_ha_state()

    @property
    def available(self):
        return self._hub.is_available()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
       return 'media-player-' + str(self._source_number_join)

    @property
    def should_poll(self):
        return False

    @property
    def device_class(self):
        return self._device_class

    @property
    def supported_features(self):
        return self._supported_features

    @property
    def state(self):
        if self._hub.get_digital(self._off_join) == 0:
            return STATE_OFF
        else:
            return STATE_ON

    @property
    def is_volume_muted(self):
        return self._hub.get_digital(self._mute_join)

    @property
    def volume_level(self):
        return self._hub.get_analog(self._volume_level_join) / 65535

    async def async_mute_volume(self, mute):
        self._hub.set_digital(self._mute_join, 1)
        await asyncio.sleep(0.05)
        self._hub.set_digital(self._mute_join, 0)

    async def async_turn_on(self):
        self._hub.set_digital(self._source_number_join, 1)
        await asyncio.sleep(0.05)
        self._hub.set_digital(self._source_number_join, 0)

    async def async_turn_off(self):
        self._hub.set_digital(self._off_join, 1)
        await asyncio.sleep(0.05)
        self._hub.set_digital(self._off_join, 0)

    async def async_volume_up(self):
        self._hub.set_digital(self._volume_up_join, 1)
        await asyncio.sleep(0.05)
        self._hub.set_digital(self._volume_up_join, 0)

    async def async_volume_down(self):
        self._hub.set_digital(self._volume_down_join, 1)
        await asyncio.sleep(0.05)
        self._hub.set_digital(self._volume_down_join, 0)
