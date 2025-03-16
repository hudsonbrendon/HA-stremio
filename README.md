# Stremio Integration for Home Assistant

This integration allows you to display top movies from Stremio in Home Assistant. It is designed to work with the [upcoming-media-card](https://github.com/custom-cards/upcoming-media-card).

## Features

- Fetches top movies from Stremio's Cinemeta API
- Filter movies by genres (Action, Comedy, Drama, etc.)
- Provides movie information in a format compatible with the upcoming-media-card
- Configurable number of movies to display

## Installation

### HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository in HACS
3. Search for "Stremio" in HACS integrations
4. Install the integration

### Manual Installation

1. Copy the `custom_components/stremio` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

### Using the UI

1. Go to **Settings** > **Devices & Services**
2. Click **+ Add Integration** and search for "Stremio"
3. Follow the configuration steps
   - Set a name for the integration
   - Choose the number of movies to display (limit)
   - Select one or more genres (optional)
   - Set the update interval

### Using Configuration.yaml

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: stremio
    name: stremio_top_movies
    limit: 10  # Optional, default is 10
    genres:  # Optional, creates a sensor for each genre
      - Action
      - Comedy
      - Drama
    scan_interval: 3600  # Optional, default is 1 hour (3600 seconds)
```

## Using with upcoming-media-card

Add a card configuration like this to your Lovelace UI:

```yaml
type: custom:upcoming-media-card
entity: sensor.stremio_top_movies
title: Top Movies on Stremio
```

If you've configured genre sensors, you can display them individually:

```yaml
type: custom:upcoming-media-card
entity: sensor.stremio_top_movies_action
title: Top Action Movies
```

## Troubleshooting

Enable debug logging in your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.stremio: debug
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.
