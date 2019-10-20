#! /usr/bin/env python3

from collections import defaultdict
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

DECO   = " "*4
DECO_2 = DECO*2

ALL_LANGS = [
    ppath.name
    for ppath in LANG_PEUF_DIR.walk("dir::")
    if ppath.parent == LANG_PEUF_DIR
]

DEFAULT_LANG = "english"

ALL_MACROS = set()

ALL_TRANS = defaultdict(dict)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

LATEX_N_OUPUT_TEMP = r"""
\begin{multicols}{2}
    \centering
    \begin{frame-gene}[Code \LaTeX]
\begin{verbatim}
\begin{algo}
<latexcode>
\end{algo}
\end{verbatim}
    \end{frame-gene}
    \vfill\null
    \columnbreak
    \textit{Mise en forme correspondante.}
\begin{algo}
<latexcode>
\end{algo}
    \vfill\null
\end{multicols}
"""

for old, new in {
    "{": '{{',
    "}": '}}',
    "<": '{',
    ">": '}',
}.items():
    LATEX_N_OUPUT_TEMP = LATEX_N_OUPUT_TEMP.replace(old, new)


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

    elif kind == "ifelif":
        kind = "IF"

    else:
        kind = kind.title()

    return f"\\SetKw{kind}"


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
    if kind in ["input", "word"]:
        tex_trans += rawgather(macroname, trans)

# \SetKwBlock{Text}{Traduction}
    elif kind == "block":
        tex_trans += rawgather(macroname, trans, suffix = "{}")

# \SetKwFor{For}{Pour}{:}{}
    elif kind == "for":
        tex_trans += rawgather(macroname, trans, suffix = "{:}{}")

# \SetKwRepeat{Repeat}{Répéter}{{Jusqu'à Avoir}}
    elif kind == "repeat":
        tex_trans.append(
            f"{macroname}{{Repeat}}{{{trans['Repeat']}}}{{{trans['Until']}}}"
        )

# \SetKwIF{If}{ElseIf}{Else}{Si}{:}{{Sinon Si}}{{Sinon}}{}
    elif kind == "ifelif":
        tex_trans.append(
            f"{macroname}{{If}}{{ElseIf}}{{Else}}{{{trans['If']}}}{{:}}"
            f"{{{trans['ElseIf']}}}{{{trans['Else']}}}{{}}"
        )

# \SetKwSwitch{Switch}{Case}{Other}{Selon}{:}{Cas}{Autre}{}
    elif kind == "switch":
        tex_trans.append(
            f"{macroname}{{Switch}}{{Case}}{{Other}}{{{trans['Switch']}}}{{:}}"
            f"{{{trans['Case']}}}{{{trans['Other']}}}{{}}"
        )

    else:
        print('', kind, trans, sep="\n");exit()

    return tex_trans


def build_tex_trans(lang):
    global ALL_TRANS

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

                ALL_TRANS[lang].update(trans)

    return tex_trans






# ------------------------- #
# -- LANG SPECIFICATIONS -- #
# ------------------------- #

TEX_TRANS = {}

for lang in ALL_LANGS:
    TEX_TRANS[lang] = build_tex_trans(lang)
    TEX_TRANS[lang] = [
        l if l.startswith("%") else DECO + l
        for l in TEX_TRANS[lang][1:]
    ]
    TEX_TRANS[lang] = "\n".join(TEX_TRANS[lang])


# -------------------- #
# -- TEXTUAL MACROS -- #
# -------------------- #

stytxtmacros = defaultdict(list)
latexmacros  = defaultdict(list)

for lang in ALL_TRANS:
    for prefix in ["TT", "AL"]:
        for control, extras in {
            "If"    : ["Else"],
            "For"   : [],
            "While" : [],
            "Repeat": ["Until"],
            "Switch": ["Case"],
        }.items():
            macroname = f"{prefix}{control.lower()}"

            if lang == "english":
                latexmacros[prefix].append(macroname)

            macrotxt  = [ ALL_TRANS[lang][control] ]
            macrotxt += [
                ALL_TRANS[lang][e]
                for e in extras
            ]

            if control == "If":
                macrotxt = "\\,--\\,".join(macrotxt)

            else:
                macrotxt = " ".join(macrotxt)

            if prefix == "TT":
                formatter = "texttt"
                macrotxt = macrotxt.upper()

            else:
                formatter = "textbf"

            stytxtmacros[lang].append(
                f"\\newcommand\\{macroname}{{\\{formatter}{{{macrotxt}}}}}"
            )

    stytxtmacros[lang] = DECO + "\n    ".join(stytxtmacros[lang])


# -------------------- #
# -- BUILD LANG STY -- #
# -------------------- #

for lang, tex_trans in TEX_TRANS.items():
    with open(
        file     = KEYWORDS_DIR / f"{lang}.sty",
        mode     = 'w',
        encoding = 'utf-8'
    ) as texlang:
        texlang.write(f"""
\\newcommand\\uselang{lang}{{
% Textual versions
{stytxtmacros[lang]}

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
    mode    = {
        'verbatim'  : ":default:",
        'keyval:: =': "titles",
    }
) as data:
    docinfos = data.mydict("std mini")

    peuftitles = docinfos["titles"]
    del docinfos["titles"]


with open(
    file     = KEYWORDS_DIR / "english.sty",
    mode     = 'r',
    encoding = 'utf-8'
) as docfile:
    lang_sty = docfile.read()


# ------------------------------------ #
# -- TEXT USEFUL MACROS - STY + DOC -- #
# ------------------------------------ #

text_start, _, text_end = between(
    text = template_tex,
    seps = [
        "% == Main tools - START == %\n",
        "\n% == Main tools - END == %"
    ],
    keepseps = True
)


texcode = []

for prefix, kind in [
    ("TT", "True Type"),
    ("AL", "algorithme"),
]:
    texcode += [
        f"""
\\begin{{center}}
	Liste des commandes de type \myquote{{{kind}}}.
\\end{{center}}

\\begin{{enumerate}}
        """.rstrip()
    ]

    for macroname in latexmacros[prefix]:
        texcode.append(
            f"{DECO}\\item \\verb+\\{macroname}+ "
            f"donne \\{macroname}."
        )

    texcode.append(
        "\\end{enumerate}"
    )

texcode = "\n".join(texcode)

template_tex = text_start + texcode + text_end


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

        if kind not in allmacros:
            allmacros[kind] = []


texdoc = []

for kind in peuftitles:
    macros = allmacros[kind]

    explanations = "\n".join(docinfos[kind])

    latexcode = []

    if kind == "input":
        lastmacro = ""
        noplurial = []

        for onemacro in macros:
            if noplurial \
            and onemacro.startswith(noplurial[-1]):
                continue

            noplurial.append(onemacro)

        for i, word in enumerate(noplurial[::2]):
            nextword = noplurial[2*i+1]

            latexcode.append(
                LATEX_N_OUPUT_TEMP.format(
                    latexcode = f"  \\{word}{{donnée 1}}\n" \
                              + f"  \\{nextword}{{donnée 2}}"
                )
            )

        latexcode = "\n".join(latexcode)


    elif kind == "block":
        nbexa     = 0

        for onemacro in macros:
            nbexa += 1

            latexcode.append(
                f"\\{onemacro}{{Instruction {nbexa}}}"
            )

    elif kind in ["for", "repeat"]:
        nbexa     = 0

        for onemacro in macros:
            nbexa += 1

            if kind == "repeat":
                nbexa = ""

            latexcode += [
                f"\\{onemacro}{{$i \\in uneliste$}}{{",
                " "*2 + f"Instruction {nbexa}",
                "}"
            ]

    elif kind == "switch":
        latexcode.append("\\Switch{$i$}{")

        prefix = "u"

        for i in range(1, 4):
            if i == 3:
                prefix = ""

            latexcode.append(
                " "*2 + f"\\{prefix}Case{{$i = {i-1}$}}{{Instruction {i}}}"
            )

        latexcode.append("}")

    elif kind == "ifelif":
         latexcode.append(
"""\\uIf{$i = 0$}{
    Instruction 1
  }
  \\uElseIf{$i = 1$}{
    Instruction 2
  }
  \\Else{
    Instruction 3
  }""")

    else:
        prefix = ""

        while macros:
            word      = macros.pop(0)
            wordlower = word.lower()

            if wordlower == "and":
                wordbis = macros.pop(0)
                latexcode.append(f"{prefix}A \\{word} B \\{wordbis} C")

            elif wordlower in ["ask", "print"]:
                latexcode.append(f"{prefix}\\{word} \"Quelque chose\"")

            elif wordlower == "return":
                latexcode.append(f"{prefix}\\{word} RÉSULTAT")

            elif wordlower.endswith("from"):
                wordbis = macros.pop(0)
                latexcode.append(f"{prefix}$k$ \\{word} $1$ \\{wordbis} $n$")

            elif wordlower == "inthis":
                latexcode.append(f"{prefix}$e$ \\{word}" + " $\{ 1 , 4 , 16 \}$")

            else:
                latexcode.append(f"{prefix}$L$ \\{word}")

            if not prefix:
                prefix = r"\\ "

    if kind != "input":
        latexcode = "\n  ".join(latexcode)
        latexcode = "  " + latexcode
        latexcode = LATEX_N_OUPUT_TEMP.format(latexcode = latexcode)

    texdoc.append(
f"""\\subsubsection{{{peuftitles[kind]}}}

{explanations}

{latexcode}
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
