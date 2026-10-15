"""SK19 Pro projector UI: serves the app's icons, installs the tuya-local device config, adds a panel."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "sk19_pro"
URL_BASE = "/sk19_pro"
DEVICE_FILE = "sk19_pro_projector.yaml"
_LOGGER = logging.getLogger(__name__)


def _install_device_config(hass: HomeAssistant) -> bool:
    """Copy the tuya-local device config into place. Returns True if it changed."""
    src = Path(__file__).parent / "tuya_local_devices" / DEVICE_FILE
    dst_dir = Path(hass.config.path("custom_components", "tuya_local", "devices"))
    if not dst_dir.is_dir():
        _LOGGER.warning("tuya_local is not installed; install it via HACS, then restart")
        return False
    dst = dst_dir / DEVICE_FILE
    data = src.read_bytes()
    if dst.exists() and dst.read_bytes() == data:
        return False
    dst.write_bytes(data)
    return True


def _asset_version() -> str:
    """Changes whenever the shipped frontend files change, so clients never run stale JS."""
    here = Path(__file__).parent
    files = [here / "frontend" / "sk19-card.js", here / "catalogue.json"]
    return str(int(max(f.stat().st_mtime for f in files)))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    here = Path(__file__).parent
    version = await hass.async_add_executor_job(_asset_version)
    module_url = f"{URL_BASE}/frontend/sk19-card.js?v={version}"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(URL_BASE, str(here), cache_headers=False)]
    )
    frontend.add_extra_js_url(hass, module_url)
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name="sk19-panel",
        frontend_url_path="sk19-projector",
        module_url=module_url,
        sidebar_title="Projector",
        sidebar_icon="mdi:movie-open-play",
        require_admin=False,
    )
    if await hass.async_add_executor_job(_install_device_config, hass):
        _LOGGER.warning(
            "Installed %s into tuya_local; restart Home Assistant to load it", DEVICE_FILE
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    frontend.async_remove_panel(hass, "sk19-projector")
    return True
