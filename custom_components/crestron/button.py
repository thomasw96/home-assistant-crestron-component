"""Platform for Crestron Button integration."""

import voluptuous as vol
import logging
import asyncio

import homeassistant.helpers.config_validation as cv
from homeassistant.components.button import ButtonEntity
from homeassistant.const import CONF_NAME
from .const import HUB, DOMAIN, CONF_BUTTON_JOIN

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_BUTTON_JOIN): cv.positive_int,
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN][HUB]
    entity = [CrestronButton(hub, config)]
    async_add_entities(entity)


class CrestronButton(ButtonEntity):
    def __init__(self, hub, config):
        self._hub = hub
        self._name = config.get(CONF_NAME)
        self._button_join = config.get(CONF_BUTTON_JOIN)

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
        return 'button-' + str(self._button_join)

    @property
    def should_poll(self):
        return False

    async def async_press(self):
        # In Crestron, button presses are modelled by triggering a signal pulse on a digital join
        self._hub.set_digital(self._button_join, True)
        await asyncio.sleep(0.2)
        self._hub.set_digital(self._button_join, False)
