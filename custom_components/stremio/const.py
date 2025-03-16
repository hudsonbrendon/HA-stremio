"""Constants for the Stremio integration."""

from datetime import timedelta
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

# Domain
DOMAIN = "stremio"

# Default values
DEFAULT_NAME = "Stremio"
DEFAULT_LIMIT = 10
DEFAULT_SCAN_INTERVAL = timedelta(hours=1)
DEFAULT_GENRES = []  # Default to no genre filters
DEFAULT_MEDIA_TYPE = "movie"  # Default to movies

# Configuration keys
CONF_LIMIT = "limit"
CONF_GENRES = "genres"
CONF_MEDIA_TYPE = "media_type"

# API
STREMIO_API_BASE_URL = {
    "movie": "https://v3-cinemeta.strem.io/catalog/movie/top",
    "series": "https://cinemeta-catalogs.strem.io/top/catalog/series/top",
}

# Available media types
MEDIA_TYPES = {
    "movie": "Filmes",
    "series": "Séries",
}

# Available genres
AVAILABLE_GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "History",
    "Horror",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Thriller",
    "War",
    "Western",
]

# Genre translations
GENRE_TRANSLATIONS = {
    "Action": "Ação",
    "Adventure": "Aventura",
    "Animation": "Animação",
    "Biography": "Biografia",
    "Comedy": "Comédia",
    "Crime": "Crime",
    "Documentary": "Documentário",
    "Drama": "Drama",
    "Family": "Família",
    "Fantasy": "Fantasia",
    "History": "História",
    "Horror": "Terror",
    "Mystery": "Mistério",
    "Romance": "Romance",
    "Sci-Fi": "Ficção Científica",
    "Sport": "Esporte",
    "Thriller": "Suspense",
    "War": "Guerra",
    "Western": "Faroeste",
    "All": "Todos",
}

# UI translations
TRANSLATIONS = {
    "name": "Nome",
    "limit": "Quantidade máxima",
    "media_type": "Tipo de mídia",
    "genres": "Gêneros",
    "scan_interval": "Intervalo de atualização (segundos)",
    "configuration_title": "Configuração do Stremio",
    "films": "Filmes",
    "series": "Séries",
}
