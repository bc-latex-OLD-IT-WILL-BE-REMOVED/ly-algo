#! /usr/bin/env python3

from mistool.latex_use import Build
from mistool.os_use import PPath

THIS_DIR = PPath( __file__ ).parent

DIR_DOC_PATH  = THIS_DIR.parent / "lyalgo"


# ----------------------- #
# -- TOOLS & CONSTANTS -- #
# ----------------------- #

DECO = " "*4

MYFRAME = lambda x: withframe(
    text  = x,
    frame = ALL_FRAMES['latex_pretty']
)


# -------------------------- #
# -- COMPILE THE DOC FILE -- #
# -------------------------- #

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
        f"{DECO}* Compilation of << {latexpath.name} >> finished."
    )
