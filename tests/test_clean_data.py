import re

import pandas as pd
import pytest

from scripts import clean_data
from scripts.clean_data import (
    check_places,
    convert_date,
    correct_communes,
    create_full_dataset,
    fill_missing_communes,
    fix_missing_communes,
    normalize_columns,
    normalize_places,
    normalize_text,
    normalize_with_hyphens,
    rename_columns,
)
from scripts.clean_data import clean_data as run_clean_data
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


def test_fill_missing_communes():
    df = pd.DataFrame(
        {"commune_normalise": ["paris", None], "dep_normalise": ["paris", "oise"]}
    )
    avant = df.copy()

    result = fill_missing_communes(df)

    assert result["commune_normalise"].tolist() == ["paris", "inconnue"]
    assert result["dep_normalise"].tolist() == ["paris", "oise"]
    pd.testing.assert_frame_equal(df, avant)


def test_fill_missing_communes_missing_column():
    with pytest.raises(KeyError, match="commune_normalise"):
        fill_missing_communes(pd.DataFrame({"autre": [1]}))


LIEN = "https://exemple.org/p/abc/"


@pytest.fixture
def fixes(monkeypatch):
    monkeypatch.setattr(clean_data, "COMMUNE_FIXES", {LIEN: "Beauvais"})


def test_fix_missing_communes_fills_empty_commune(fixes):
    df = pd.DataFrame({"commune": [None, "Lyon"], "lien_instagram": [LIEN, "autre"]})
    avant = df.copy()

    result = fix_missing_communes(df)

    assert result["commune"].tolist() == ["Beauvais", "Lyon"]
    pd.testing.assert_frame_equal(df, avant)


def test_fix_missing_communes_keeps_existing_commune(fixes):
    """Source corrigée entre-temps : la valeur de la source l'emporte."""
    df = pd.DataFrame({"commune": ["Compiègne"], "lien_instagram": [LIEN]})

    assert fix_missing_communes(df)["commune"].tolist() == ["Compiègne"]


def test_fix_missing_communes_unknown_link_raises(fixes):
    df = pd.DataFrame({"commune": [None], "lien_instagram": ["autre"]})

    with pytest.raises(ValueError, match="0 ligne"):
        fix_missing_communes(df)


def test_fix_missing_communes_ambiguous_link_raises(fixes):
    df = pd.DataFrame({"commune": [None, None], "lien_instagram": [LIEN, LIEN]})

    with pytest.raises(ValueError, match="2 ligne"):
        fix_missing_communes(df)


def test_fix_missing_communes_missing_column(fixes):
    with pytest.raises(KeyError, match="lien_instagram"):
        fix_missing_communes(pd.DataFrame({"commune": [None]}))


def test_normalize_with_hyphens():
    noms = pd.Series(["Saint Étienne", "Saint-Laurent-d\u2019Arce", "L'Isle", None])

    result = normalize_with_hyphens(noms)

    assert result.tolist()[:3] == ["saint-etienne", "saint-laurent-d-arce", "l-isle"]
    assert pd.isna(result[3])


def places(communes, deps):
    return pd.DataFrame({"commune_normalise": communes, "dep_normalise": deps})


@pytest.mark.parametrize(
    ("commune", "dep", "attendu"),
    [
        ("13e-arrondissement", "paris", "paris"),
        ("1er-arrondissement", "paris", "paris"),
        ("3e-arrondissement", "bouches-du-rhone", "3e-arrondissement"),
        ("marseille-3e-arrondissement", "paris", "marseille-3e-arrondissement"),
        ("tremolat-", "dordogne", "tremolat"),
        ("-lyon ", "rhone", "lyon"),
    ],
)
def test_normalize_places_communes(commune, dep, attendu):
    result = normalize_places(places([commune], [dep]))

    assert result["commune_normalise"].tolist() == [attendu]


def test_normalize_places_bourgoin_jallieu():
    result = normalize_places(places(["bourgoin-jallieu-/-lyon"], ["rhone"]))

    assert result["commune_normalise"].tolist() == ["bourgoin-jallieu"]
    assert result["dep_normalise"].tolist() == ["isere"]


def test_normalize_places_strips_department():
    result = normalize_places(places(["lyon"], ["-rhone-"]))

    assert result["dep_normalise"].tolist() == ["rhone"]


def test_normalize_places_keeps_missing_values():
    result = normalize_places(places([None, "lyon"], ["oise", "rhone"]))

    assert pd.isna(result.loc[0, "commune_normalise"])
    assert result.loc[1, "commune_normalise"] == "lyon"


def test_normalize_places_does_not_modify_input():
    df = places(["13e-arrondissement ", "bourgoin-jallieu-/-lyon"], ["paris", "rhone"])
    avant = df.copy()

    result = normalize_places(df)

    pd.testing.assert_frame_equal(df, avant)
    assert result is not df


def test_normalize_places_missing_column():
    with pytest.raises(KeyError, match="commune_normalise"):
        normalize_places(pd.DataFrame({"dep_normalise": ["paris"]}))


def test_correct_communes(monkeypatch):
    monkeypatch.setattr(clean_data, "COMMUNE_CORRECTIONS", {"paris-(18e)": "paris"})
    df = places(["paris-(18e)", "lyon", None], ["paris", "rhone", "oise"])
    avant = df.copy()

    result = correct_communes(df)

    assert result["commune_normalise"].tolist()[:2] == ["paris", "lyon"]
    assert pd.isna(result.loc[2, "commune_normalise"])
    pd.testing.assert_frame_equal(df, avant)


def test_correct_communes_missing_column():
    with pytest.raises(KeyError, match="commune_normalise"):
        correct_communes(pd.DataFrame({"autre": [1]}))


def test_check_places_valid():
    check_places(places(["paris", "inconnue"], ["paris", "oise"]))


def test_check_places_missing_commune():
    with pytest.raises(ValueError, match=r"commune_normalise manquant.*\[1\]"):
        check_places(places(["paris", None], ["paris", "oise"]))


def test_check_places_missing_department():
    with pytest.raises(ValueError, match=r"dep_normalise manquant.*\[0\]"):
        check_places(places(["paris"], [None]))


@pytest.mark.parametrize("nom", ["paris-(18e)", "equilivaz/la-salle"])
def test_check_places_suspect_commune(nom):
    with pytest.raises(ValueError, match=re.escape(nom)):
        check_places(places([nom], ["paris"]))


RAW_COLUMNS = "QUAND,LIEU,DÉPARTEMENT,LIEN INSTAGRAM\n"


def write_raw(directory, lignes, year="2025"):
    (directory / f"feminicide_{year}.csv").write_text(RAW_COLUMNS + lignes)


def test_clean_data_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(clean_data, "COMMUNE_FIXES", {"lien-a": "Beauvais"})
    write_raw(
        tmp_path,
        "01/01/2025,Saint Étienne,Loire,lien-b\n"
        "02/01/2025,,Oise,lien-a\n"
        "03/01/2025,Paris (18e),Paris,lien-c\n"
        "04/01/2025,13e arrondissement,Paris,lien-d\n",
    )

    df = run_clean_data(tmp_path)

    assert df["commune_normalise"].tolist() == [
        "saint-etienne",
        "beauvais",
        "paris",
        "paris",
    ]
    assert df["dep_normalise"].tolist() == ["loire", "oise", "paris", "paris"]
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_clean_data_unknown_commune_when_no_fix(tmp_path, monkeypatch):
    monkeypatch.setattr(clean_data, "COMMUNE_FIXES", {})
    write_raw(tmp_path, "01/01/2025,Lyon,Rhône,lien-b\n02/01/2025,,Oise,lien-a\n")

    result = run_clean_data(tmp_path)

    assert result["commune_normalise"].tolist() == ["lyon", "inconnue"]


def test_clean_data_fails_on_unlisted_suspect_commune(tmp_path, monkeypatch):
    monkeypatch.setattr(clean_data, "COMMUNE_FIXES", {})
    write_raw(tmp_path, "02/01/2025,Nouvelle (Annexe),Oise,lien-a\n")

    with pytest.raises(ValueError, match="COMMUNE_CORRECTIONS"):
        run_clean_data(tmp_path)


def test_clean_data_fails_on_bad_date(tmp_path, monkeypatch):
    monkeypatch.setattr(clean_data, "COMMUNE_FIXES", {})
    write_raw(tmp_path, "2025-01-02,Lyon,Rhône,lien-a\n")

    with pytest.raises(ValueError, match="date"):
        run_clean_data(tmp_path)


def test_main_writes_interim_file(tmp_path, monkeypatch):
    df = places(["paris"], ["paris"])
    monkeypatch.setattr(clean_data, "clean_data", lambda: df)
    monkeypatch.setattr(clean_data, "INTERIM_DIR", tmp_path / "interim")

    clean_data.main()

    ecrit = pd.read_csv(tmp_path / "interim" / "feminicide_clean.csv")
    assert ecrit["commune_normalise"].tolist() == ["paris"]


def test_main_writes_nothing_on_failure(tmp_path, monkeypatch):
    def echec():
        raise ValueError("boom")

    monkeypatch.setattr(clean_data, "clean_data", echec)
    monkeypatch.setattr(clean_data, "INTERIM_DIR", tmp_path / "interim")

    with pytest.raises(ValueError, match="boom"):
        clean_data.main()

    assert not (tmp_path / "interim").exists()
