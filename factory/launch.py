# gestion de [en] et [fr]

#!/usr/bin/env python3

# --------------------- #
# -- SEVERAL IMPORTS -- #
# --------------------- #

from mistool.os_use import PPath, runthis


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_FILE = PPath(__file__)
THIS_DIR  = THIS_FILE.parent


# -------------------------------------- #
# -- LAUNCHING ALL THE BUILDING TOOLS -- #
# -------------------------------------- #

for pattern in [
    "file::**build-*.py",
    "file::build-*.py"
]:
    allpaths = [onepath for onepath in THIS_DIR.walk(pattern)]
    allpaths.sort()

    for onepath in allpaths:
        filename = (onepath - THIS_DIR).stem

        if filename[7].isdigit():
            comment = ""

        else:
            comment = "  [this is a sub builder]"

        print(f'+ Launching "{filename}"{comment}')


        runthis(
            cmd        = 'python "{0}"'.format(onepath),
            showoutput = True
        )
