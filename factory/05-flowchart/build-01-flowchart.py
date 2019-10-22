#! /usr/bin/env python3

from mistool.os_use import PPath

THIS_DIR = PPath(__file__).parent

THIS_EXA_DIR = THIS_DIR / "examples"
EXA_DIR_DEST = THIS_DIR.parent.parent / "lyalgo" / "examples"

# -------------------------------- #
# -- COPYING FILES FOR EXAMPLES -- #
# -------------------------------- #

for peufpath in THIS_EXA_DIR.walk("file::**.tkz"):
    peufpath.copy_to(
        dest     = EXA_DIR_DEST / (peufpath - THIS_EXA_DIR),
        safemode = False
    )
