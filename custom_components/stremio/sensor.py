"""Sensor platform for Stremio integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import dt as dt_util

from .const import (
    AVAILABLE_GENRES,
    CONF_GENRES,
    CONF_LIMIT,
    CONF_MEDIA_TYPE,
    DEFAULT_GENRES,
    DEFAULT_LIMIT,
    DEFAULT_MEDIA_TYPE,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    GENRE_TRANSLATIONS,
    LOGGER,
    MEDIA_TYPES,
    STREMIO_API_BASE_URL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_LIMIT, default=DEFAULT_LIMIT): cv.positive_int,
        vol.Optional(CONF_MEDIA_TYPE, default=DEFAULT_MEDIA_TYPE): vol.In(
            list(MEDIA_TYPES.keys())
        ),
        vol.Optional(CONF_GENRES, default=DEFAULT_GENRES): vol.All(
            cv.ensure_list, [vol.In(AVAILABLE_GENRES)]
        ),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Stremio sensor."""
    name = config.get(CONF_NAME)
    limit = config.get(CONF_LIMIT)
    media_type = config.get(CONF_MEDIA_TYPE, DEFAULT_MEDIA_TYPE)
    genres = config.get(CONF_GENRES, [])

    entities = []

    if not genres:
        # Create a default sensor with no genre filter
        entities.append(StremioSensor(None, name, limit, media_type, None))
    else:
        # Create a sensor for each genre
        for genre in genres:
            genre_name = f"{name} - {GENRE_TRANSLATIONS.get(genre, genre)}"
            entities.append(StremioSensor(None, genre_name, limit, media_type, genre))

    async_add_entities(entities, True)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Stremio sensor from a config entry."""
    config = hass.data[DOMAIN][entry.entry_id]
    limit = config.get(CONF_LIMIT)
    media_type = config.get(CONF_MEDIA_TYPE, DEFAULT_MEDIA_TYPE)
    genres = config.get(CONF_GENRES, [])

    # Set standardized name based on media type
    media_type_name = MEDIA_TYPES.get(media_type, media_type.capitalize())
    base_name = f"Stremio {media_type_name}"

    entities = []

    if not genres:
        # Create a default sensor with no genre filter if no genres selected
        sensor_name = base_name
        LOGGER.debug(
            "Criando sensor Stremio padrão sem filtro de gênero: %s", sensor_name
        )
        entities.append(
            StremioSensor(entry.entry_id, sensor_name, limit, media_type, None)
        )
    else:
        # Create a sensor for each selected genre
        for genre in genres:
            genre_name_pt = GENRE_TRANSLATIONS.get(genre, genre)
            sensor_name = f"{base_name} - {genre_name_pt}"
            LOGGER.debug("Criando sensor Stremio para gênero: %s", genre_name_pt)
            entities.append(
                StremioSensor(entry.entry_id, sensor_name, limit, media_type, genre)
            )

    async_add_entities(entities, True)


class StremioSensor(SensorEntity):
    """Representation of a Stremio sensor."""

    _attr_icon = "mdi:play-circle"
    _attr_has_entity_name = True  # Enable entity registry name handling

    def __init__(
        self,
        entry_id: str | None,
        name: str,
        limit: int,
        media_type: str,
        genre: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        self._entry_id = entry_id
        self._limit = limit
        self._media_type = media_type
        self._genre = genre
        self._state = None
        self._attributes = {}

        # Set appropriate icon based on media type
        self._attr_icon = "mdi:movie" if media_type == "movie" else "mdi:television"

        # Create unique ID based on entry_id, media_type, and genre
        genre_suffix = f"_{genre.lower()}" if genre else ""
        media_suffix = f"_{media_type}"
        if entry_id:
            self._attr_unique_id = f"{entry_id}{media_suffix}{genre_suffix}"
        else:
            self._attr_unique_id = f"{DOMAIN}_{media_type}{genre_suffix}"

        # Set entity name to only show the genre (or "All" if no genre)
        if genre:
            self._attr_name = GENRE_TRANSLATIONS.get(genre, genre)
        else:
            self._attr_name = "Todos"

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return self._attributes

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Stremio instance."""
        if not self._entry_id:
            return None

        # Set standard device name based on media type
        media_type_name = MEDIA_TYPES.get(
            self._media_type, self._media_type.capitalize()
        )
        device_name = f"Stremio {media_type_name}"

        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry_id}_{self._media_type}")},
            name=device_name,
            manufacturer="Stremio",
            model="Integration",
        )

    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            async with async_timeout.timeout(10):
                items = await self._fetch_stremio_items()

            if not items:
                _LOGGER.error("Nenhum item encontrado")
                return

            # Limit the number of items
            items = items[: self._limit]

            # Format the items for upcoming-media-card
            card_items = []
            for item in items:
                try:
                    formatted_item = self._format_item_for_upcoming_media_card(item)
                    card_items.append(formatted_item)
                except Exception as err:  # pylint: disable=broad-except
                    _LOGGER.error("Erro formatando item %s: %s", item.get("name"), err)

            self._state = len(card_items)

            # Set up attributes in the exact structure upcoming-media-card expects
            self._attributes = {
                "data": card_items,
                "media_type": self._media_type,
                "count": len(card_items),
            }

            # Add genre information to attributes if we're filtering
            if self._genre:
                self._attributes["genre"] = self._genre
                self._attributes["genre_name"] = GENRE_TRANSLATIONS.get(
                    self._genre, self._genre
                )

            # Log successful update
            media_type_name = MEDIA_TYPES.get(self._media_type, self._media_type)
            genre_info = (
                f" no gênero {GENRE_TRANSLATIONS.get(self._genre, self._genre)}"
                if self._genre
                else ""
            )

            _LOGGER.debug(
                "Atualização do Stremio concluída, encontrados %s %s%s",
                self._state,
                media_type_name.lower(),
                genre_info,
            )

        except TimeoutError:
            _LOGGER.error("Tempo esgotado ao buscar dados do Stremio")
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Erro ao atualizar sensor do Stremio: %s", err)

    async def _fetch_stremio_items(self) -> list[dict[str, Any]]:
        """Fetch items from Stremio API."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "DNT": "1",
            "Referer": "https://web.stremio.com/",
        }

        # Build the API URL based on whether we have a genre filter
        base_url = STREMIO_API_BASE_URL.get(
            self._media_type, STREMIO_API_BASE_URL["movie"]
        )

        if self._genre:
            api_url = f"{base_url}/genre={self._genre}.json"
        else:
            api_url = f"{base_url}.json"

        _LOGGER.debug("Buscando dados do Stremio da URL: %s", api_url)

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()

                if not data.get("metas"):
                    _LOGGER.error("Resposta inválida da API do Stremio: %s", data)
                    return []

                return data.get("metas", [])

    def _format_item_for_upcoming_media_card(
        self, item: dict[str, Any]
    ) -> dict[str, Any]:
        """Format item data for upcoming-media-card."""
        poster = item.get("poster", "")
        # Extract the year from the ID (format: tt123456:year)
        item_id_parts = item.get("id", "").split(":")
        year = item_id_parts[1] if len(item_id_parts) > 1 else None

        # Default values for required fields
        now = dt_util.now()

        # Format the poster URLs
        if poster and not poster.startswith(("http:", "https:")):
            poster = f"https:{poster}"

        backdrop = item.get("background", "")
        if backdrop and not backdrop.startswith(("http:", "https:")):
            backdrop = f"https:{backdrop}"

        # Handle director field - ensure it's a list before joining
        directors = item.get("director", ["Desconhecido"])
        if not isinstance(directors, list):
            directors = [str(directors)] if directors else ["Desconhecido"]

        # Handle genre field - ensure it's a list before joining
        genres = item.get("genre", [])
        if not isinstance(genres, list):
            genres = [str(genres)] if genres else []

        # Basic item info
        result = {
            "airdate": now.strftime("%Y-%m-%d"),
            "aired": now.strftime("%Y-%m-%d"),
            "release": now.strftime("%Y-%m-%d"),
            "poster": poster,
            "fanart": backdrop,
            "title": item.get("name", "Desconhecido"),
            "runtime": item.get("runtime", 0),
            "rating": item.get("imdbRating", 0),
            "year": year,
            "studio": ", ".join(directors),
            "genres": ", ".join([GENRE_TRANSLATIONS.get(g, g) for g in genres]),
            "plot": item.get("description", ""),
        }

        # Add TV series specific data
        if self._media_type == "series":
            result.update(
                {
                    "episode": item.get("episodeCount", 1),
                    "seasons": item.get("seasonCount", 1),
                    "status": item.get("status", "Finalizada"),
                }
            )

        else:
            # For movies
            result.update(
                {
                    "in_cinemas": year,
                    "release_date": year,
                }
            )

        return result
