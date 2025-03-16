# Stremio Integration for Home Assistant

This integration allows you to display top movies and TV series from Stremio in Home Assistant. It is designed to work with the [upcoming-media-card](https://github.com/custom-cards/upcoming-media-card) to create an attractive media discovery experience in your dashboard.

## Features

- Fetches top movies and TV series from Stremio's Cinemeta API
- Filter content by genres (Action, Comedy, Drama, etc.)
- Creates individual sensors for each genre you select
- Provides media information in a format compatible with the upcoming-media-card
- Configurable number of items to display
- Automatic device organization based on media type

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
   - Choose the media type (movies or series)
   - Set the number of items to display (limit)
   - Select one or more genres (optional)
   - Set the update interval

### Using Configuration.yaml

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: stremio
    name: stremio_top_movies
    media_type: movie  # Options: movie, series
    limit: 10  # Optional, default is 10
    genres:  # Optional, creates a sensor for each genre
      - Action
      - Comedy
      - Drama
    scan_interval: 3600  # Optional, default is 1 hour (3600 seconds)
```

## Sensors & Devices

The integration creates:

- **Devices**: One device per media type (Stremio Movies, Stremio Series)
- **Sensors**:
  - If no genres are selected, a single sensor named "Todos" (All) is created
  - If genres are selected, a separate sensor is created for each genre
  - Each sensor shows the number of available items as its state
  - Sensors contain all media data in their attributes

Sensor naming examples:
- `sensor.all` - All movies/series
- `sensor.action` - Action movies/series
- `sensor.comedy` - Comedy movies/series

## Using with upcoming-media-card

Add a card configuration like this to your Lovelace UI:

```yaml
type: custom:upcoming-media-card
entity: sensor.all
title: Top Movies on Stremio
```

For genre-specific sensors:

```yaml
type: custom:upcoming-media-card
entity: sensor.action
title: Top Action Movies
```

## Sensor Attributes

Each sensor has the following attributes:
- `data`: List of media items with details (title, poster, plot, etc.)
- `media_type`: Type of media (movie or series)
- `genre`: Genre code (if filtering by genre)
- `genre_name`: Genre name (if filtering by genre)

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
