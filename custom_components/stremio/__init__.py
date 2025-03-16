"""Stremio integration for Home Assistant."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as get_device_registry
from homeassistant.helpers.entity_registry import async_get as get_entity_registry

from .const import (
    CONF_GENRES,
    CONF_LIMIT,
    CONF_MEDIA_TYPE,
    DEFAULT_GENRES,
    DEFAULT_LIMIT,
    DEFAULT_MEDIA_TYPE,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
    MEDIA_TYPES,
)

# Update platforms to include entity platform
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Stremio from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Store configuration in hass.data
    genres = entry.options.get(CONF_GENRES, entry.data.get(CONF_GENRES, DEFAULT_GENRES))
    media_type = entry.options.get(
        CONF_MEDIA_TYPE, entry.data.get(CONF_MEDIA_TYPE, DEFAULT_MEDIA_TYPE)
    )

    # Create a base configuration for all sensors
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_NAME: entry.data.get(CONF_NAME, DEFAULT_NAME),
        CONF_LIMIT: entry.options.get(
            CONF_LIMIT, entry.data.get(CONF_LIMIT, DEFAULT_LIMIT)
        ),
        CONF_SCAN_INTERVAL: entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL.total_seconds()),
        ),
        CONF_GENRES: genres,
        CONF_MEDIA_TYPE: media_type,
    }

    # Register a device for this integration
    device_registry = get_device_registry(hass)
    media_type_name = MEDIA_TYPES.get(media_type, media_type.capitalize())
    device_name = f"Stremio {media_type_name}"

    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{entry.entry_id}_{media_type}")},
        name=device_name,
        manufacturer="Stremio",
        model="Integration",
        sw_version="1.0",
    )

    LOGGER.debug(
        "Configurando integração Stremio com nome: %s, limite: %s, tipo de mídia: %s, gêneros: %s",
        hass.data[DOMAIN][entry.entry_id][CONF_NAME],
        hass.data[DOMAIN][entry.entry_id][CONF_LIMIT],
        media_type_name,
        hass.data[DOMAIN][entry.entry_id][CONF_GENRES],
    )

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update when config_entry options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup(hass: HomeAssistant, config) -> bool:
    """Set up the Stremio integration."""
    return True
