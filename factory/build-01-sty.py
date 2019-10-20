#! /usr/bin/env python3

from collections import defaultdict

from mistool.os_use import PPath
from mistool.string_use import between, joinand
from mistool.term_use import ALL_FRAMES, withframe
from orpyste.data import ReadBlock

# ----------------------- #
# -- TOOLS & CONSTANTS -- #
# ----------------------- #

THIS_DIR = PPath( __file__ ).parent

STY_PATH   = THIS_DIR.parent / "lyalgo" / "lyalgo.sty"


DECO = " "*4

MYFRAME = lambda x: withframe(
    text  = x,
    frame = ALL_FRAMES['latex_pretty']
)


def path2title(onepath):
    onepath = relative_path.stem.replace('-', ' ').upper()

    while onepath[0] in " 0123456789":
        onepath = onepath[1:]

    return onepath


def cleansource(text):
    if text.strip():
        text = text.split("\n")

        for i in [0, -1]:
            while not text[i].strip():
                text.pop(i)

    else:
        text = []

    return "\n".join(text)


def organize_packages(packages):
    global DECO

    packages_found = defaultdict(list)

    for texpackdef in packages:
        if texpackdef:
            options = between(
                text = texpackdef,
                seps = ["[", "]"]
            )

            if options:
                _, options, texpackdef = options

                options = [x.strip() for x in options.split(",")]

            else:
                options = []

            _, names, _ = between(
                text = texpackdef,
                seps = ["{", "}"]
            )

            for onename in names.split(","):
                packages_found[onename.strip()] += options

    allnames = sorted(packages_found.keys())

    packages_ok = []

    for onename in allnames:
        options = packages_found[onename]
        options = set(options)

        if options:
            options = f'{",".join(options)}'

            packages_ok.append(f"\\PassOptionsToPackage{{{options}}}{{{onename}}}")

        packages_ok.append(f"\\RequirePackage{{{onename}}}")


    print(f"{DECO}* Declaration of packages organized.")

    return packages_ok


# ---------------- #
# -- NEW THINGS -- #
# ---------------- #

ALL_PACKAGES       = []
ALL_MACROS         = []
ALL_LOCAL_SETTINGS = []

paths_found = []
for subdir in THIS_DIR.walk("dir::"):
    subdir_name = str(subdir.name)

    if subdir_name in [
        "config",
    ] or subdir_name[:2] == "x-":
        continue

    for latexfile in subdir.walk("file::*.sty"):
        if latexfile.name[0] in "0123456789":
            paths_found.append(latexfile)


paths_found.sort()

for latexfile in paths_found:
    relative_path = latexfile - THIS_DIR
    parentname    = latexfile.parent.name

    print(f"{DECO}* Analyzing << {relative_path} >>")

    with open(
        file     = latexfile,
        encoding = "utf-8"
    ) as filetoupdate:
        _, packages, definitions = between(
            text = filetoupdate.read(),
            seps = [
                "% == PACKAGES USED == %",
                "% == DEFINITIONS == %"
            ],
            keepseps = False
        )

    ALL_PACKAGES += [
        x.strip()
        for x in packages.strip().split("\n")
    ]


    definitions = cleansource(definitions)


    if definitions.strip():
        if ALL_MACROS:
            ALL_MACROS.append("\n")

        ALL_MACROS += [
            MYFRAME(path2title(relative_path.stem)),
            "",
            definitions
        ]


ALL_MACROS = "\n".join(ALL_MACROS)


# --------------------------------- #
# -- ORGANIZING LIST OF PACKAGES -- #
# --------------------------------- #

ALL_PACKAGES = organize_packages(ALL_PACKAGES)


# ------------------------------ #
# -- UPDATE THE MAIN STY FILE -- #
# ------------------------------ #

ALL_PACKAGES = "\n".join(ALL_PACKAGES)

source = f"""{MYFRAME("PACKAGES REQUIRED")}

{ALL_PACKAGES}


{ALL_MACROS}
"""

STY_PATH.create("file")

with STY_PATH.open(
    mode     = "w",
    encoding = "utf-8"
) as lyxam:
    lyxam.write(source)

print(f"{DECO}* Update of << {STY_PATH.name} >> done.")
