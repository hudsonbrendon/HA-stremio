"""Config flow for Stremio integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers import selector

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
    MEDIA_TYPES,
    TRANSLATIONS,
)


class StremioConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Stremio."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Ensure genres is always a list, even if none selected
            genres = user_input.get(CONF_GENRES, DEFAULT_GENRES)
            user_input[CONF_GENRES] = genres if genres else []

            # Check if we already have an instance with the same media type
            media_type = user_input.get(CONF_MEDIA_TYPE, DEFAULT_MEDIA_TYPE)

            # Look for existing entries with the same media type and genres
            for entry in self._async_current_entries():
                if entry.data.get(CONF_MEDIA_TYPE) == media_type and set(
                    entry.data.get(CONF_GENRES, [])
                ) == set(user_input[CONF_GENRES]):
                    errors["base"] = "media_type_genre_already_configured"
                    break

            if not errors:
                # Create title based on media type only, without adding genres
                media_type_name = MEDIA_TYPES.get(media_type, media_type.capitalize())
                title = f"Stremio {media_type_name}"

                return self.async_create_entry(
                    title=title,
                    data=user_input,
                )

        # Prepare translated genre options for selector
        genre_options = [
            {"label": GENRE_TRANSLATIONS.get(genre, genre), "value": genre}
            for genre in AVAILABLE_GENRES
        ]

        # Prepare media type options for selector
        media_type_options = [
            {"label": label, "value": value} for value, label in MEDIA_TYPES.items()
        ]

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_NAME,
                    default=DEFAULT_NAME,
                    description={"suggested_value": DEFAULT_NAME},
                ): str,
                vol.Optional(
                    CONF_MEDIA_TYPE,
                    default=DEFAULT_MEDIA_TYPE,
                    description={"suggested_value": DEFAULT_MEDIA_TYPE},
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=media_type_options,
                        multiple=False,
                        custom_value=False,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="media_type",
                    )
                ),
                vol.Optional(
                    CONF_LIMIT,
                    default=DEFAULT_LIMIT,
                    description={"suggested_value": DEFAULT_LIMIT},
                ): vol.All(int, vol.Range(min=1, max=50)),
                vol.Optional(
                    CONF_GENRES,
                    default=DEFAULT_GENRES,
                    description={"suggested_value": DEFAULT_GENRES},
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=genre_options,
                        multiple=True,
                        custom_value=False,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="genres",
                    )
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_SCAN_INTERVAL.total_seconds(),
                    description={
                        "suggested_value": DEFAULT_SCAN_INTERVAL.total_seconds()
                    },
                ): vol.All(int, vol.Range(min=300, max=86400)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders=TRANSLATIONS,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return StremioOptionsFlow(config_entry)


class StremioOptionsFlow(config_entries.OptionsFlow):
    """Config flow options handler for Stremio."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Ensure genres is always a list, even if none selected
            genres = user_input.get(CONF_GENRES, [])
            user_input[CONF_GENRES] = genres if genres else []

            # Check for duplicates if media type was changed
            media_type = user_input.get(CONF_MEDIA_TYPE)
            current_media_type = self._config_entry.data.get(CONF_MEDIA_TYPE)

            if media_type != current_media_type:
                # Look for existing entries with the same media type and genres
                for entry in self.hass.config_entries.async_entries(DOMAIN):
                    if (
                        entry.entry_id != self._config_entry.entry_id
                        and entry.data.get(CONF_MEDIA_TYPE) == media_type
                        and set(entry.data.get(CONF_GENRES, []))
                        == set(user_input[CONF_GENRES])
                    ):
                        errors["base"] = "media_type_genre_already_configured"
                        break

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        current_genres = self._config_entry.options.get(
            CONF_GENRES, self._config_entry.data.get(CONF_GENRES, DEFAULT_GENRES)
        )

        current_media_type = self._config_entry.options.get(
            CONF_MEDIA_TYPE,
            self._config_entry.data.get(CONF_MEDIA_TYPE, DEFAULT_MEDIA_TYPE),
        )

        # Prepare translated genre options for selector
        genre_options = [
            {"label": GENRE_TRANSLATIONS.get(genre, genre), "value": genre}
            for genre in AVAILABLE_GENRES
        ]

        # Prepare media type options for selector
        media_type_options = [
            {"label": label, "value": value} for value, label in MEDIA_TYPES.items()
        ]

        options = {
            vol.Optional(
                CONF_MEDIA_TYPE,
                default=current_media_type,
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=media_type_options,
                    multiple=False,
                    custom_value=False,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    translation_key="media_type",
                )
            ),
            vol.Optional(
                CONF_LIMIT,
                default=self._config_entry.options.get(
                    CONF_LIMIT, self._config_entry.data.get(CONF_LIMIT, DEFAULT_LIMIT)
                ),
            ): vol.All(int, vol.Range(min=1, max=50)),
            vol.Optional(
                CONF_GENRES,
                default=current_genres,
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=genre_options,
                    multiple=True,
                    custom_value=False,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    translation_key="genres",
                )
            ),
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self._config_entry.options.get(
                    CONF_SCAN_INTERVAL,
                    self._config_entry.data.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL.total_seconds()
                    ),
                ),
            ): vol.All(int, vol.Range(min=300, max=86400)),
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(options),
            errors=errors,
            description_placeholders=TRANSLATIONS,
        )
