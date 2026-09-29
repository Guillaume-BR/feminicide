"""Télécharge les CSV bruts de féminicides depuis l'API data.gouv.fr.

Remplace les URLs codées en dur : les ressources annuelles sont découvertes
automatiquement via le champ `resources[]` du jeu de données, en repérant
l'année dans le titre de chaque ressource (ex. « ... féminicides 2026 »).
"""

import json
import re
from pathlib import Path

import requests

DATASET_API_URL = (
    "https://www.data.gouv.fr/api/1/datasets/decompte-et-recensement-des-feminicides/"
)
YEAR_PATTERN = re.compile(r"féminicides (\d{4})")
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "fetch_state.json"


def get_yearly_resources() -> dict[str, dict[str, str]]:
    """Retourne {année: url_csv} pour chaque ressource annuelle du jeu de données."""
    response = requests.get(DATASET_API_URL, timeout=30)
    response.raise_for_status()
    resources = response.json()["resources"]

    yearly_urls = {}
    for resource in resources:
        match = YEAR_PATTERN.search(resource["title"])
        if match:
            yearly_urls[match.group(1)] = {}
            yearly_urls[match.group(1)]["url"] = resource["url"]
            yearly_urls[match.group(1)]["last_modified"] = resource["last_modified"]
    return yearly_urls


def download_resource(year: str, url: str, dest_dir: Path = RAW_DIR) -> Path:
    """Télécharge le CSV d'une année et le sauvegarde dans dest_dir."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"feminicide_{year}.csv"
    dest_path.write_bytes(response.content)
    return dest_path


def save_state(path: Path, state: dict[str, str]) -> None:
    """Sauvegarde la date de dernière modification des ressources annuelles dans un fichier JSON."""
    path.write_text(json.dumps(state, indent=2))


def load_state(path: Path) -> dict[str, str]:
    """Charge la date de dernière modification des ressources annuelles depuis un fichier JSON.
    Retourne un dictionnaire {année: last_modified}."""
    if path.exists():
        return json.loads(path.read_text())
    else:
        return {}


def main() -> None:
    yearly_urls = get_yearly_resources()
    print(f"Found {len(yearly_urls)} yearly resources")
    state = load_state(STATE_PATH)
    print(f"Loaded state: {state}")
    for year in sorted(yearly_urls):
        if yearly_urls[year]["last_modified"] == state.get(year, ""):
            print(f"{year}: already up to date")
            continue
        dest_path = download_resource(year, yearly_urls[year]["url"])
        print(f"{year}: {dest_path}")
        state[year] = yearly_urls[year]["last_modified"]

    save_state(STATE_PATH, state)


if __name__ == "__main__":
    main()
