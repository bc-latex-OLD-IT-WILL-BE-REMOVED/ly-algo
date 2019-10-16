#! /usr/bin/env python3

import re

from mistool.os_use import PPath
from mistool.string_use import between, joinand
from orpyste.data import ReadBlock

BASENAME = PPath(__file__).stem.replace("build-", "")
THIS_DIR = PPath(__file__).parent

STY_FILE = THIS_DIR / f'{BASENAME}.sty'
TEX_FILE = STY_FILE.parent / (STY_FILE.stem + "[fr].tex")

KEYWORDS_FINAL_DIR = THIS_DIR.parent.parent / "lyalgo" / "keywords"
KEYWORDS_DIR       = THIS_DIR / "keywords"
LANG_PEUF_DIR      = KEYWORDS_DIR / "config"

DECO = " "*4

ALL_LANGS = [
    ppath.name
    for ppath in LANG_PEUF_DIR.walk("dir::")
    if ppath.parent == LANG_PEUF_DIR
]

DEFAULT_LANG = "english"

ALL_MACROS = set()


# ----------- #
# -- TOOLS -- #
# ----------- #

def protect(word):
    word = word.strip()

    if " " in word:
        word = f"{{{word}}}"

    return word


def normalize(trans):
    for word, wtrans in trans.items():
        ALL_MACROS.add(word)

# Auto tranlation !
        if not wtrans:
            lastchar = word[-1]

            if lastchar in ["s", "m"]:
                basename = word[:-1]

                if basename in trans:
                    if lastchar == "m":
                        lastchar = ""

                    wtrans = trans[basename] + lastchar.lower()

                else:
                    wtrans = word

            else:
                wtrans = word

# Add the translation
        trans[word] = wtrans

# Protect and split translations
    for word, wtrans in trans.items():
        if " " in wtrans:
            wtrans = protect(wtrans)

        trans[word] = wtrans

# Nothing more to do.
    return trans


def macrodef(kind):
    if kind == "word":
        kind = ""

    return f"\\SetKw{kind.title()}"


def rawgather(macroname, trans, suffix = ""):
    tex_trans = []

    for word, wtrans in trans.items():
        tex_trans.append(
            f"{macroname}{{{word}}}{{{wtrans}}}{suffix}"
        )

    return tex_trans


def texify(kind, trans):
    tex_trans = [
        '',
        '% ' + kind.title(),
    ]

# Common def
    macroname = f"{macrodef(kind)}"

# \SetKw{Text}{Traduction}
    if kind in ["block", "input", "word"]:
        tex_trans += rawgather(macroname, trans)

# \SetKwFor{For}{Pour}{:}{}
    elif kind == "for":
        tex_trans += rawgather(macroname, trans, suffix = "{:}{}")

# \SetKwRepeat{Repeat}{Répéter}{{Jusqu'à Avoir}}
    elif kind == "repeat":
        tex_trans.append(
            f"{macroname}{{Repeat}}{{{trans['Repeat']}}}{{{trans['Until']}}}"
        )

# \SetKwIF{If}{ElseIf}{Else}{Si}{:}{{Sinon Si}}{{Sinon}}{:}
    elif kind == "ifelif":
        tex_trans.append(
            f"{macroname}{{If}}{{ElseIf}}{{Else}}{{{trans['If']}}}{{:}}"
            f"{{{trans['ElseIf']}}}{{{trans['Else']}}}{{:}}"
        )

# \SetKwSwitch{Switch}{Case}{Other}{Selon}{:}{Cas}{Autre}{:}
    elif kind == "switch":
        tex_trans.append(
            f"{macroname}{{Switch}}{{Case}}{{Other}}{{{trans['Switch']}}}{{:}}"
            f"{{{trans['Case']}}}{{{trans['Other']}}}{{:}}"
        )

    else:
        print('', kind, trans, sep="\n");exit()

    return tex_trans


def build_tex_trans(lang):
    tex_trans = []

    for peufpath in (
        LANG_PEUF_DIR / lang
    ).walk("file::*.peuf"):
        with ReadBlock(
            content = peufpath,
            mode    = 'keyval:: ='
        ) as data:
            for kind, trans in data.mydict("std mini").items():
                trans      = normalize(trans)
                tex_trans += texify(kind, trans)

    return tex_trans


# ------------------------- #
# -- LANG SPECIFICATIONS -- #
# ------------------------- #

for onelang in ALL_LANGS:
    tex_trans = build_tex_trans(onelang)
    tex_trans = [
        l if l.startswith("%") else DECO + l
        for l in tex_trans[1:]
    ]
    tex_trans = "\n".join(tex_trans)

    with open(
        file     = KEYWORDS_DIR / f"{onelang}.sty",
        mode     = 'w',
        encoding = 'utf-8'
    ) as texlang:
        texlang.write(f"""
\\newcommand\\uselang{onelang}{{
{tex_trans}
}}
        """.lstrip())


# --------------------------------------- #
# -- COPY LANG STY TO THE FINAL FOLDER -- #
# --------------------------------------- #

KEYWORDS_FINAL_DIR.create("dir")

for peufpath in (KEYWORDS_DIR).walk("file::*.sty"):
    peufpath.copy_to(
        dest     = KEYWORDS_FINAL_DIR / peufpath.name,
        safemode = False
    )


# ------------------------- #
# -- TEMPLATES TO UPDATE -- #
# ------------------------- #

with open(
    file     = TEX_FILE,
    mode     = 'r',
    encoding = 'utf-8'
) as docfile:
    template_tex = docfile.read()


with ReadBlock(
    content = KEYWORDS_DIR / "config" / "for-doc[fr].peuf",
    mode    = 'keyval:: ='
) as data:
    titles = data.mydict("std mini")["titles"]


with open(
    file     = KEYWORDS_DIR / "english.sty",
    mode     = 'r',
    encoding = 'utf-8'
) as docfile:
    lang_sty = docfile.read()


# ------------------ #
# -- UPDATING DOC -- #
# ------------------ #

text_start, _, text_end = between(
    text = template_tex,
    seps = [
        "% == All extra words - START == %\n",
        "\n% == All extra words - END == %"
    ],
    keepseps = True
)

allmacros = {}

pattern_kwmacro = re.compile("\\SetKw(.*?)\{(.*?)\}")

for oneline in lang_sty.split("\n"):
    match = re.search(pattern_kwmacro, oneline)

    if match:
        allmacros[kind].append(match.group(2))

    elif oneline.startswith("%"):
        kind = oneline[1:].strip().lower()
        kind = titles[kind]

        if kind not in allmacros:
            allmacros[kind] = []

textitles = []

for kind in titles:
    newtitle = titles[kind]

    if newtitle not in textitles:
        textitles.append(newtitle)


texdoc = []

for title in textitles:
    macros = allmacros[title]
    # macros.sort()

    texdoc.append(
f"""\\subsubsection{{{title}}}

\\begin{{multicols}}{{2}}
{macros}
\\vfill\\null
\\end{{multicols}}
"""
    )

texdoc = "\n".join(texdoc)


template_tex = text_start + texdoc + text_end


with open(
    file     = TEX_FILE,
    mode     = 'w',
    encoding = 'utf-8'
) as docfile:
    docfile.write(template_tex)
