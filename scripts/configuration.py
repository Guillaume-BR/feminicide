"""Fichier contenant toutes les constantes de configuration du projet,
notamment les chemins vers les fichiers de référence
"""

import re
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# Nom des CSV bruts : feminicide_<année>.csv (le groupe capture l'année)
FILENAME_PATTERN = re.compile(r"feminicide_(\d{4})\.csv")

# Arrondissement parisien seul, une fois le nom normalisé : « 13e-arrondissement »,
# « 1er-arrondissement » (le nom de la ville n'est pas dans la source)
ARRONDISSEMENT_PATTERN = r"\d{1,2}(?:er|e)-arrondissement"

# Corrections manuelles de communes, une fois le nom normalisé (clé) -> nom officiel.
# Ce sont des noms avec précision entre parenthèses ou barre oblique dans la source.
# Corné est une commune déléguée de Loire-Authion (nom officiel en 2025).
COMMUNE_CORRECTIONS = {
    "paris-(18e)": "paris",
    "corne-(loire-authion)": "loire-authion",
    "saint-pierre-(ravine-des-cabris)": "saint-pierre",
    "mamoudzou-(m-tsapere)": "mamoudzou",
    "dunkerque-(malo-les-bains)": "dunkerque",
    "equilivaz/la-salle": "equilivaz-la-salle",  # hors de France
}

# Communes manquantes dans la source : lien Instagram de la publication (unique) -> commune.
# S'applique uniquement si la commune est vide ; à vider quand la source est corrigée.
COMMUNE_FIXES = {
    "https://www.instagram.com/p/DUOpjAnjOZg/": "Beauvais",  # Mathilde, 17/05/2025
}

# Valeur donnée à une commune absente de la source (jamais jointe à un fichier de communes)
UNKNOWN_COMMUNE = "inconnue"

# Dossier des données intermédiaires (jamais lu par l'application Streamlit)
INTERIM_DIR = Path(__file__).resolve().parent.parent / "data" / "interim"

# Caractères que NFKD + encodage ASCII supprimeraient en silence (ou déformeraient).
# À appliquer AVANT la normalisation, sur du texte déjà en minuscules : seules les
# minuscules sont donc listées (œ, æ, ß, ø, ł, đ ; leurs majuscules passent par lower()).
# Clés : un seul caractère, écrit en échappement Unicode (\uXXXX).
SPECIAL_CHARS = {
    # apostrophes et signes assimilés -> apostrophe droite
    "\u2018": "'",  # guillemet simple ouvrant
    "\u2019": "'",  # apostrophe typographique
    "\u201b": "'",  # guillemet simple haut inversé
    "\u02bc": "'",  # lettre apostrophe (Wallis-et-Futuna, etc.)
    "\u02bb": "'",  # lettre okina (Polynésie)
    "\u2032": "'",  # prime
    "\u00b4": "'",  # accent aigu isolé
    # tirets et signes assimilés -> trait d'union
    "\u2010": "-",  # trait d'union
    "\u2011": "-",  # trait d'union insécable
    "\u2012": "-",  # tiret numérique
    "\u2013": "-",  # demi-cadratin
    "\u2014": "-",  # cadratin
    "\u2015": "-",  # barre horizontale
    "\u2212": "-",  # signe moins
    # guillemets -> guillemet droit
    "\u201c": '"',  # guillemet double ouvrant (anglais)
    "\u201d": '"',  # guillemet double fermant (anglais)
    "\u201e": '"',  # guillemet double bas
    "\u00ab": '"',  # guillemet français ouvrant
    "\u00bb": '"',  # guillemet français fermant
    # ligatures et lettres sans décomposition Unicode
    "\u0153": "oe",  # ligature oe
    "\u00e6": "ae",  # ligature ae
    "\u00df": "ss",  # eszett
    "\u00f8": "o",  # o barré
    "\u0142": "l",  # l barré
    "\u0111": "d",  # d barré
    # signes à supprimer
    "\u00b0": "",  # degré (N° -> n)
    "\u00ba": "",  # indicateur ordinal masculin (Nº -> n, comme N°)
    "\N{SOFT HYPHEN}": "",  # trait d'union conditionnel (invisible)
    "\N{ZERO WIDTH SPACE}": "",  # espace de largeur nulle (invisible)
    "\N{ZERO WIDTH NON-JOINER}": "",  # antiliant de largeur nulle (invisible)
    "\N{ZERO WIDTH JOINER}": "",  # liant de largeur nulle (invisible)
    "\N{ZERO WIDTH NO-BREAK SPACE}": "",  # BOM / espace insécable de largeur nulle (invisible)
    # séparateur de ligne -> espace
    "\N{LINE SEPARATOR}": " ",
}

# Table prête pour str.translate
SPECIAL_CHARS_TABLE = str.maketrans(SPECIAL_CHARS)
