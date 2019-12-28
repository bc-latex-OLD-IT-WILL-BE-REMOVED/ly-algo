#! /usr/bin/env python3

from collections import defaultdict

from mistool.latex_use import install, PPath

DECO = " "*4

answer = input(f"{DECO}* Local installation ? [y/n] ")

if answer.lower() == "y":
    THIS_DIR = PPath( __file__ ).parent

    install(ppath = THIS_DIR.parent / "lyalgo")

    print(f"{DECO}* Installation has been done.")
