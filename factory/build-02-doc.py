#! /usr/bin/env python3

from collections import defaultdict

from mistool.latex_use import Build, clean as latexclean
from mistool.os_use import cd, PPath, runthis
from mistool.string_use import between, case, joinand, MultiReplace
from mistool.term_use import ALL_FRAMES, withframe
from orpyste.data import ReadBlock

THIS_DIR = PPath( __file__ ).parent

TEMPLATE_PATH = THIS_DIR / "config" / "doc[fr].tex"
DIR_DOC_PATH  = THIS_DIR.parent / "lyalgo"
DOC_PATH      = DIR_DOC_PATH / "lyalgo-doc[fr].tex"
EXA_DIR_DEST  = DIR_DOC_PATH / "examples"

DOUBLE_BRACES = MultiReplace({
    '{': '{{',
    '}': '}}'
})

PYFORMAT = MultiReplace({
    '%((': '{',
    '))%': '}'
})


# ----------------------- #
# -- TOOLS & CONSTANTS -- #
# ----------------------- #

DECO = " "*4

MYFRAME = lambda x: withframe(
    text  = x,
    frame = ALL_FRAMES['latex_pretty']
)


# ------------ #
# -- HEADER -- #
# ------------ #

with open(
    file     = THIS_DIR / "config" / "header[fr].sty",
    encoding = "utf-8"
) as headerfile:
    HEADER = headerfile.read().strip()


# ---------------------- #
# -- LOOKING FOR DOCS -- #
# ---------------------- #

CONTENTS      = []
EXAMPLE_FILES = []
LATEXFILES    = []

for subdir in THIS_DIR.walk("dir::"):
    subdir_name = str(subdir.name)
    subdir_str  = str(subdir)

    if subdir_name in ["config", "style"] \
    or "x-" in subdir_str:
        continue

    LATEXFILES += [
        l for l in subdir.walk("file::*\[fr\].tex")
        if not l.stem.endswith("-nodoc[fr]")
    ]

    subdir_exa = subdir / "examples"

    EXAMPLE_FILES += [
        (l, subdir_exa) for l in subdir.walk("file::examples/**")
    ]

LATEXFILES.sort()

for latexfile in LATEXFILES:
    with latexfile.open(
        mode     = "r",
        encoding = "utf-8"
    ) as texfile:
        _, content, _ = between(
            text = texfile.read(),
            seps = [
                r"\begin{document}",
                r"\end{document}"
            ]
        )

        CONTENTS.append(content)


for peufpath, subdir_exa in EXAMPLE_FILES:
    peufpath.copy_to(
        dest     = EXA_DIR_DEST / (peufpath - subdir_exa),
        safemode = False
    )


# ------------------------- #
# -- UPDATE THE DOC FILE -- #
# ------------------------- #

with TEMPLATE_PATH.open(
    mode     = "r",
    encoding = "utf-8"
) as docfile:
    content = DOUBLE_BRACES(docfile.read())
    content = PYFORMAT(content)
    content = content.format(
        header  = HEADER,
        content = "\n".join(CONTENTS)
    )


with DOC_PATH.open(
    mode     = "w",
    encoding = "utf-8"
) as docfile:
    docfile.write(content)


print(f"{DECO}* Update of << {DOC_PATH.name} >> done.")


# ------------------------------- #
# -- COMPILE ALL THE DOCS FILE -- #
# ------------------------------- #

nbrepeat = 3

for latexpath in DIR_DOC_PATH.walk(f"file::*.tex"):
    print(
        f"{DECO}* Compilations of << {latexpath.name} >> started : {nbrepeat} times."
    )

    builder = Build(
        ppath      = latexpath,
        repeat     = nbrepeat,
        showoutput = True
    )
    builder.pdf()

    print(
        f"{DECO}* Compilation of << {latexpath.name} >> finished.",
        f"{DECO}* Cleaning extra files.",
        sep = "\n"
    )

latexclean(DIR_DOC_PATH)
