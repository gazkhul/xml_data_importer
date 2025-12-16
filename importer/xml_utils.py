from pathlib import Path


def get_xml_files(directory_path: str) -> list[Path]:
    watch_dir = Path(directory_path)
    return list(watch_dir.glob("*.xml"))
