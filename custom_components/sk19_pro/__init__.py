"""SK19 Pro projector UI: serves the app's icons, installs the tuya-local device config, adds a panel."""
from __future__ import annotations

import logging
from pathlib import Path

from aiohttp import web

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import HomeAssistantView, StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "sk19_pro"
URL_BASE = "/sk19_pro"
DEVICE_FILE = "sk19_pro_projector.yaml"
_LOGGER = logging.getLogger(__name__)


class _NoCacheFileView(HomeAssistantView):
    """Serve one frontend file with Cache-Control: no-cache so clients always revalidate.

    Static paths get heuristic caching; without this, a card update would be invisible
    to an already-loaded client until its cache expired.
    """

    requires_auth = False

    def __init__(self, hass: HomeAssistant, url: str, path: Path, content_type: str) -> None:
        self.url = url
        self.name = "api:sk19_pro:" + url.rsplit("/", 1)[-1].replace(".", "_")
        self._hass = hass
        self._path = path
        self._content_type = content_type

    async def get(self, request: web.Request) -> web.Response:
        body = await self._hass.async_add_executor_job(self._path.read_bytes)
        return web.Response(
            body=body,
            content_type=self._content_type,
            headers={"Cache-Control": "no-cache"},
        )


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


DASHBOARD_URL_PATH = "sk19-dashboard"


def _dashboard_exists(hass: HomeAssistant) -> bool:
    """True if the user created the Projector dashboard (it then owns the sidebar entry)."""
    try:
        data = hass.data.get("lovelace")
        dashboards = getattr(data, "dashboards", None)
        if dashboards is None and isinstance(data, dict):
            dashboards = data.get("dashboards")
        return DASHBOARD_URL_PATH in (dashboards or {})
    except Exception:  # noqa: BLE001 - best effort
        return False


async def _ensure_lovelace_resource(hass: HomeAssistant, url: str) -> bool:
    """Register the card script as a Lovelace resource (storage mode only).

    Resources are loaded and awaited before dashboards render their cards, which
    avoids the "Custom element doesn't exist" race on slow clients. Best effort:
    this relies on HA internals, so any failure just falls back to extra_js_url.
    """
    try:
        data = hass.data.get("lovelace")
        resources = getattr(data, "resources", None)
        if resources is None and isinstance(data, dict):
            resources = data.get("resources")
        if resources is None or not hasattr(resources, "async_create_item"):
            return False  # YAML-mode resources are read-only
        await resources.async_get_info()  # makes sure storage is loaded
        for item in list(resources.async_items()):
            if str(item.get("url", "")).split("?")[0] == f"{URL_BASE}/frontend/sk19-card.js":
                if item.get("url") != url:
                    await resources.async_update_item(item["id"], {"res_type": "module", "url": url})
                return True
        await resources.async_create_item({"res_type": "module", "url": url})
        return True
    except Exception:  # noqa: BLE001 - never block setup on a convenience feature
        _LOGGER.debug("Could not register Lovelace resource", exc_info=True)
        return False


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    here = Path(__file__).parent
    version = await hass.async_add_executor_job(_asset_version)
    module_url = f"{URL_BASE}/frontend/sk19-card.js?v={version}"
    if not hass.data.get(f"{DOMAIN}_views"):
        # registered before the static path so these exact URLs win the route match
        for rel, ctype in (("frontend/sk19-card.js", "application/javascript"), ("catalogue.json", "application/json")):
            hass.http.register_view(_NoCacheFileView(hass, f"{URL_BASE}/{rel}", here / rel, ctype))
        hass.data[f"{DOMAIN}_views"] = True
    await hass.http.async_register_static_paths(
        [StaticPathConfig(URL_BASE, str(here), cache_headers=False)]
    )
    frontend.add_extra_js_url(hass, module_url)
    await _ensure_lovelace_resource(hass, module_url)
    # With the dashboard present, it owns the sidebar entry (per-user sidebar settings
    # would otherwise show both). The panel stays reachable at /sk19-projector.
    in_sidebar = not _dashboard_exists(hass)
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name="sk19-panel",
        frontend_url_path="sk19-projector",
        module_url=module_url,
        sidebar_title="Projector" if in_sidebar else None,
        sidebar_icon="mdi:movie-open-play" if in_sidebar else None,
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
