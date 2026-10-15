"""One-click config flow for the SK19 Pro projector UI."""
from homeassistant import config_entries

from . import DOMAIN


class SK19ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title="SK19 Pro Projector", data={})
        return self.async_show_form(step_id="user")
