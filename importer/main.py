from importer.logger import logger
from importer.settings import WATCH_DIR


def main():
    logger.info(f"Watching directory: {WATCH_DIR}")
    logger.error("This is an error message")


if __name__ == "__main__":
    main()
