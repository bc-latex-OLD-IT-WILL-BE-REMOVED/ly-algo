#! /usr/bin/env python3

from mistool.latex_use import clean as latexclean
from mistool.os_use import PPath


# ----------------------- #
# -- TOOLS & CONSTANTS -- #
# ----------------------- #

FACTORY_DIR = PPath( __file__ ).parent
LYBOOK_DIR  = FACTORY_DIR.parent / "lyalgo"

# ----------------------- #
# -- CLEAN BEFORE PUSH -- #
# ----------------------- #

latexclean(LYBOOK_DIR)
