#! /usr/bin/env python3

from mistool.latex_use import clean as latexclean
from mistool.os_use import PPath


# ----------------------- #
# -- TOOLS & CONSTANTS -- #
# ----------------------- #

FACTORY_DIR = PPath( __file__ ).parent
LYXAM_DIR   = FACTORY_DIR.parent / "lyalgo"


# ----------------------- #
# -- CLEAN BEFORE PUSH -- #
# ----------------------- #

for toremove in FACTORY_DIR.walk("file::**.macros-x.txt"):
    toremove.remove()

for toremove in LYXAM_DIR.walk("file::*.macros-x.txt"):
    toremove.remove()

for toremove in FACTORY_DIR.walk("file::**.pdf"):
    toremove.remove()

for toremove in FACTORY_DIR.walk("dir::*"):
    latexclean(toremove)
