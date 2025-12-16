from loguru import logger

from importer.settings import LOGGER_CONFIG


logger.add(
    LOGGER_CONFIG["file_path"],
    rotation=LOGGER_CONFIG["rotation"],
    retention=LOGGER_CONFIG["retention"],
    compression=LOGGER_CONFIG["compression"],
    level=LOGGER_CONFIG["level"],
)
