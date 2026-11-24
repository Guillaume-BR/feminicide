import re

import pandas as pd
import pytest

from scripts.clean_data import (
    convert_date,
    create_full_dataset,
    normalize_columns,
    normalize_text,
    rename_columns,
)
from scripts.configuration import SPECIAL_CHARS

CSV_CONTENT = "QUAND,LIEU\n01/01/{year},Paris\n02/01/{year},Lyon\n"


def write_csv(directory, name, year="2022"):
    (directory / name).write_text(CSV_CONTENT.format(year=year))


def test_create_full_dataset_concatenates_and_adds_year(tmp_path):
    write_csv(tmp_path, "feminicide_2022.csv", "2022")
    write_csv(tmp_path, "feminicide_2023.csv", "2023")

    df = create_full_dataset(tmp_path)

    assert len(df) == 4
    assert list(df["year"].unique()) == ["2022", "2023"]
    assert (df.loc[df["year"] == "2023", "QUAND"].str.endswith("2023")).all()


def test_create_full_dataset_is_sorted_by_filename(tmp_path):
    write_csv(tmp_path, "feminicide_2024.csv", "2024")
    write_csv(tmp_path, "feminicide_2022.csv", "2022")

    df = create_full_dataset(tmp_path)

    assert list(df["year"].unique()) == ["2022", "2024"]


def test_create_full_dataset_empty_directory(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_full_dataset(tmp_path)


def test_create_full_dataset_ignores_unrelated_files(tmp_path):
    write_csv(tmp_path, "feminicide_2022.csv", "2022")
    write_csv(tmp_path, "autre.csv")

    df = create_full_dataset(tmp_path)

    assert len(df) == 2


def test_create_full_dataset_invalid_filename_without_year(tmp_path):
    write_csv(tmp_path, "feminicide_2022.csv", "2022")
    write_csv(tmp_path, "feminicide_test.csv")

    with pytest.raises(ValueError, match="feminicide_test.csv"):
        create_full_dataset(tmp_path)


@pytest.mark.parametrize(
    ("texte", "attendu"),
    [
        # accents et cédille
        ("Élève", "eleve"),
        ("Ça va?", "ca va?"),
        ("À l'école", "a l'ecole"),
        ("Café", "cafe"),
        ("façade", "facade"),
        # apostrophe typographique -> apostrophe droite
        ("Saint-Laurent-d\u2019Arce", "saint-laurent-d'arce"),
        # demi-cadratin -> trait d'union (le strip se fait ailleurs)
        ("Massy\u2013Palaiseau ", "massy-palaiseau "),
        ("\u2013", "-"),
        # ligatures et lettres sans décomposition Unicode
        ("C\u0153uvres-et-Valsery", "coeuvres-et-valsery"),
        ("Œuvre", "oeuvre"),  # majuscule : lower() doit passer avant translate
        ("Stra\u00dfe", "strasse"),
        # guillemets français -> guillemets droits
        ("\u00ab test \u00bb", '" test "'),
        # signes supprimés : N° et Nº donnent le même résultat
        ("N\u00b0", "n"),
        ("N\u00ba", "n"),
        ("A\N{ZERO WIDTH SPACE}B", "ab"),  # espace de largeur nulle
        # séparateur de ligne -> espace
        ("x\N{LINE SEPARATOR}y", "x y"),
        # cas limite
        ("", ""),
    ],
)
def test_normalize_text(texte, attendu):
    assert normalize_text(texte) == attendu


@pytest.mark.parametrize(("caractere", "remplacement"), SPECIAL_CHARS.items())
def test_normalize_text_applies_every_special_char(caractere, remplacement):
    """Chaque entrée du dictionnaire est bien appliquée, quelle que soit sa position."""
    assert normalize_text(f"a{caractere}b") == f"a{remplacement}b"


def test_special_chars_replacements_are_ascii():
    """Une valeur non ASCII serait supprimée en silence par l'encodage ASCII."""
    assert all(valeur.isascii() for valeur in SPECIAL_CHARS.values())


def test_normalize_columns():
    df = pd.DataFrame(
        {
            "Nom": ["Élève", "Ça va?", "À l'école"],
            "Âge": [10, 12, 11],
            "Ville": ["Paris", "Lyon", "Marseille"],
        }
    )

    cleaned_df = normalize_columns(df)

    assert list(cleaned_df.columns) == ["nom", "age", "ville"]
    assert cleaned_df["nom"].tolist() == ["Élève", "Ça va?", "À l'école"]


def test_normalize_columns_raw_headers():
    """En-têtes réels des CSV #NousToutes : espaces, accents et signe degré."""
    brut = [
        "QUAND",
        "LIEU",
        "DÉPARTEMENT",
        "PRÉNOM",
        "ÂGE",
        "N\u00b0",
        "CONTENU PUBLICATION",
        "LIEN INSTAGRAM",
    ]
    df = pd.DataFrame(columns=brut)

    cleaned_df = normalize_columns(df)

    assert list(cleaned_df.columns) == [
        "quand",
        "lieu",
        "departement",
        "prenom",
        "age",
        "n",
        "contenu_publication",
        "lien_instagram",
    ]


def test_normalize_columns_does_not_modify_input():
    df = pd.DataFrame(columns=["CONTENU PUBLICATION", "N\u00b0"])

    normalize_columns(df)

    assert list(df.columns) == ["CONTENU PUBLICATION", "N\u00b0"]


def test_normalize_columns_strips_surrounding_spaces():
    df = pd.DataFrame(columns=[" Nom de ville "])

    assert list(normalize_columns(df).columns) == ["nom_de_ville"]


def test_rename_columns():
    df = pd.DataFrame({"quand": ["2022"], "lieu": ["paris"], "n": [4]})
    result = rename_columns(df)
    assert list(result.columns) == ["date", "commune"]


def test_rename_columns_missing_quand():
    df = pd.DataFrame({"quan": ["2022"], "lieu": ["paris"], "n": [4]})
    with pytest.raises(KeyError, match="Absence de la colonne 'quand'"):
        rename_columns(df)


def test_rename_columns_missing_lieu():
    df = pd.DataFrame({"quand": ["2022"], "lieux": ["paris"], "n": [4]})
    with pytest.raises(KeyError, match="Absence de la colonne 'quand' ou 'lieu'"):
        rename_columns(df)


def test_convert_date_with_good_df():
    df_good = pd.DataFrame(
        {
            "date": [
                "25/04/2025",
                "26/04/2025",
            ]
        }
    )
    avant = df_good.copy()
    good_result = convert_date(df_good)
    pd.testing.assert_frame_equal(df_good, avant)
    assert "date_brute" not in df_good.columns
    assert pd.api.types.is_datetime64_any_dtype(good_result["date"])
    assert good_result["date"].tolist() == [
        pd.Timestamp("2025-04-25"),
        pd.Timestamp("2025-04-26"),
    ]


def test_convert_date_with_wrong_df():
    df_wrong1 = pd.DataFrame({"quand": ["25/04/2025", "25-04-2025"]})
    with pytest.raises(KeyError, match="Absence de la colonne"):
        convert_date(df_wrong1)

    df_wrong2 = pd.DataFrame(
        {
            "date": ["25/04/2025", "25-04-2025", "abc"],
            "commune": ["paris", "paris", "paris"],
            "year": [2022, 2022, 2022],
        }
    )
    with pytest.raises(ValueError, match=re.escape("2 date(s) au mauvais format")):
        convert_date(df_wrong2)
