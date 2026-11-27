"""
Nettoie les données pour le projet de recherche sur le féminicide.
"""

from pathlib import Path
from unicodedata import normalize

import pandas as pd

from scripts.configuration import (
    ARRONDISSEMENT_PATTERN,
    COMMUNE_CORRECTIONS,
    COMMUNE_FIXES,
    FILENAME_PATTERN,
    INTERIM_DIR,
    RAW_DIR,
    SPECIAL_CHARS_TABLE,
    UNKNOWN_COMMUNE,
)


def create_full_dataset(path: Path = RAW_DIR) -> pd.DataFrame:
    """Crée le dataset complet à partir des fichiers bruts.

    Les colonnes restent brutes (non normalisées) ; une colonne `year` (str)
    est ajoutée à partir du nom de fichier `feminicide_<année>.csv`.

    Args: path: Répertoire contenant les fichiers CSV bruts.

    Returns: DataFrame concaténé de tous les fichiers CSV bruts.

    Raises:
        - FileNotFoundError: Si aucun fichier CSV n'est trouvé dans le répertoire.
        - ValueError: Si un fichier CSV a un nom invalide (ne contenant pas l'année
    """
    all_files = sorted(path.glob("feminicide_*.csv"))
    if not all_files:
        raise FileNotFoundError(f"Aucun fichier CSV trouvé dans {path}")
    dataframes = []
    for file in all_files:
        match = FILENAME_PATTERN.fullmatch(file.name)
        if match is None:
            raise ValueError(f"Impossible d'extraire l'année du nom de fichier {file}")
        df_year = pd.read_csv(file)
        df_year["year"] = match.group(1)
        dataframes.append(df_year)
    return pd.concat(dataframes, ignore_index=True)


def normalize_text(text: str) -> str:
    """Renvoie le texte en minuscules, sans accent ni cédille.

    Args: text: Texte à normaliser.

    Returns: Texte normalisé.
    """
    text = text.lower().translate(SPECIAL_CHARS_TABLE)
    return normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise les colonnes du DataFrame.

    - Remplace les espaces par des underscores.
    - Normalise le nom des colonnes

    Args: df: DataFrame à nettoyer.

    Returns: DataFrame nettoyé.
    """
    # Renommage des noms des colonnes : minuscules, espaces remplacés par des underscores, accents supprimés
    df = df.rename(columns=lambda x: normalize_text(x).strip().replace(" ", "_"))
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renomme et supprime certaines colonnes du df.

    Args : Dataframe à nettoyer

    Returns : Dataframe nettoyé

    Raises : KeyError si la colonne 'quand' ou 'lieu' est manquante
    """
    if "quand" not in df.columns or "lieu" not in df.columns:
        raise KeyError("Absence de la colonne 'quand' ou 'lieu'")
    else:
        df = df.rename(columns={"quand": "date", "lieu": "commune"})

    df = df.drop(columns=["n"], errors="ignore")
    return df


def fix_missing_communes(df: pd.DataFrame) -> pd.DataFrame:
    """Renseigne les communes manquantes de la source via `COMMUNE_FIXES`.

    Chaque correction est identifiée par le lien Instagram de la publication.
    Une commune déjà renseignée n'est jamais remplacée.

    Args: df: DataFrame avec les colonnes `commune` et `lien_instagram`.

    Returns: Copie corrigée du DataFrame (l'entrée n'est pas modifiée).

    Raises:
        - KeyError: Si `commune` ou `lien_instagram` est absente.
        - ValueError: Si un lien de `COMMUNE_FIXES` ne correspond pas à exactement
          une ligne (correction obsolète ou lien ambigu).
    """
    if "commune" not in df.columns or "lien_instagram" not in df.columns:
        raise KeyError("Colonne(s) 'commune' ou 'lien_instagram' absente(s).")

    df = df.copy()
    for lien, commune in COMMUNE_FIXES.items():
        masque = df["lien_instagram"] == lien
        if masque.sum() != 1:
            raise ValueError(
                f"{masque.sum()} ligne(s) pour le lien {lien} (1 attendue) : "
                "corriger COMMUNE_FIXES."
            )
        df.loc[masque & df["commune"].isna(), "commune"] = commune
    return df


def convert_date(df: pd.DataFrame) -> pd.DataFrame:
    """Convertis la colonne 'date' au bon format.

    Args : Dataframe à convertir

    Returns : Dataframe converti

    Raises :
        - KeyError si la colonne 'date' est manquante.
        - ValueError si certaines dates n'ont pas pu être convertie.
    """
    if "date" not in df.columns:
        raise KeyError("Absence de la colonne 'date'.")

    df = df.copy()
    df["date_brute"] = df["date"]
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    masque = df["date"].isna()
    if masque.any():
        wrong_date = df.loc[masque, ["date_brute", "commune", "year"]]
        raise ValueError(
            f"{masque.sum()} date(s) au mauvais format : {wrong_date.head()}."
        )

    df = df.drop(["date_brute"], axis=1)
    return df


def normalize_places(df: pd.DataFrame) -> pd.DataFrame:
    """Applique les corrections propres aux noms de communes et de départements.

    - Retire les espaces et tirets en début et en fin de nom.
    - Remplace un arrondissement parisien seul (« 13e arrondissement ») par `paris`,
      uniquement si le département est Paris.
    - Corrige le cas `bourgoin-jallieu-/-lyon` (commune de l'Isère).

    Args: df: DataFrame avec les colonnes `commune_normalise` et `dep_normalise`.

    Returns: Copie corrigée du DataFrame (l'entrée n'est pas modifiée).

    Raises: KeyError: Si `commune_normalise` ou `dep_normalise` est absente.
    """
    if "commune_normalise" not in df.columns or "dep_normalise" not in df.columns:
        raise KeyError(
            "Colonne(s) 'commune_normalise' ou 'dep_normalise' absente(s) des données."
        )

    df = df.copy()

    # suppression des espaces et tirets au début et à la fin
    for col in ("commune_normalise", "dep_normalise"):
        df[col] = df[col].str.strip("- ")

    # arrondissement parisien seul -> paris (pas pour Marseille ou Lyon, par exemple)
    arrondissement = df["commune_normalise"].str.fullmatch(
        ARRONDISSEMENT_PATTERN, na=False
    ) & (df["dep_normalise"] == "paris")
    df.loc[arrondissement, "commune_normalise"] = "paris"

    # cas particulier de bourgoin-jallieu-/-lyon, qui est en Isère
    df["commune_normalise"] = df["commune_normalise"].str.replace(
        "bourgoin-jallieu-/-lyon", "bourgoin-jallieu", regex=False
    )
    df.loc[df["commune_normalise"] == "bourgoin-jallieu", "dep_normalise"] = "isere"

    return df


def normalize_with_hyphens(names: pd.Series) -> pd.Series:
    """Normalise des noms de lieux : minuscules, sans accent, espaces et apostrophes -> tirets.

    Les valeurs manquantes restent manquantes.
    """
    return (
        names.map(normalize_text, na_action="ignore")
        .str.replace(" ", "-", regex=False)
        .str.replace("'", "-", regex=False)
    )


def correct_communes(df: pd.DataFrame) -> pd.DataFrame:
    """Applique les corrections manuelles de `COMMUNE_CORRECTIONS` aux communes.

    Args: df: DataFrame avec la colonne `commune_normalise`.

    Returns: Copie corrigée du DataFrame (l'entrée n'est pas modifiée).

    Raises: KeyError: Si `commune_normalise` est absente.
    """
    if "commune_normalise" not in df.columns:
        raise KeyError("Colonne 'commune_normalise' absente des données.")
    df = df.copy()
    df["commune_normalise"] = df["commune_normalise"].replace(COMMUNE_CORRECTIONS)
    return df


def fill_missing_communes(df: pd.DataFrame) -> pd.DataFrame:
    """Remplace une commune manquante par `UNKNOWN_COMMUNE`.

    Le département reste renseigné : la ligne compte dans les totaux par département.

    Args: df: DataFrame avec la colonne `commune_normalise`.

    Returns: Copie corrigée du DataFrame (l'entrée n'est pas modifiée).

    Raises: KeyError: Si `commune_normalise` est absente.
    """
    if "commune_normalise" not in df.columns:
        raise KeyError("Colonne 'commune_normalise' absente des données.")
    df = df.copy()
    df["commune_normalise"] = df["commune_normalise"].fillna(UNKNOWN_COMMUNE)
    return df


def check_places(df: pd.DataFrame) -> None:
    """Vérifie que les communes et départements sont exploitables.

    Raises: ValueError: Si une commune ou un département est manquant, ou si une
        commune contient encore des parenthèses ou une barre oblique (à ajouter
        à `COMMUNE_CORRECTIONS`).
    """
    for col in ("commune_normalise", "dep_normalise"):
        manquants = df.index[df[col].isna()].tolist()
        if manquants:
            raise ValueError(f"{col} manquant aux lignes {manquants}.")
    suspects = df["commune_normalise"].str.contains(r"[()/]", regex=True)
    if suspects.any():
        noms = sorted(df.loc[suspects, "commune_normalise"].unique())
        raise ValueError(f"Communes à ajouter à COMMUNE_CORRECTIONS : {noms}.")


def clean_data(path: Path = RAW_DIR) -> pd.DataFrame:
    """Enchaîne toutes les étapes de nettoyage et vérifie le résultat.

    Raises: les erreurs des étapes (fichiers, colonnes, dates, lieux).
    """
    df = create_full_dataset(path)
    df = normalize_columns(df)
    df = rename_columns(df)
    df = fix_missing_communes(df)
    df = convert_date(df)
    df["commune_normalise"] = normalize_with_hyphens(df["commune"])
    df["dep_normalise"] = normalize_with_hyphens(df["departement"])
    df = normalize_places(df)
    df = correct_communes(df)
    df = fill_missing_communes(df)
    check_places(df)
    return df


def main() -> None:
    """Nettoie les données et les écrit dans `data/interim/`.

    Rien n'est écrit si une étape échoue : `data/processed/` (lu par le site)
    n'est jamais touché ici.
    """
    df = clean_data()
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(INTERIM_DIR / "feminicide_clean.csv", index=False)


if __name__ == "__main__":
    main()
