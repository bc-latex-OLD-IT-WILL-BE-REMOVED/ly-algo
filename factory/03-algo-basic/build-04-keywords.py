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

THIS_EXA_DIR       = THIS_DIR / "examples" / "algo-basic" / "additional-macros"
LATEX_N_OUPUT_TEMP = """
\\begin{{algo}}
{latexcode}
\\end{{algo}}
""".lstrip()

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


# --------------------------------------- #
# -- PREPARING THE UPDATING OF THE DOC -- #
# --------------------------------------- #

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


latexcodes = defaultdict(list)

for kind in peuftitles:
    macros = allmacros[kind]

    if kind == "input":
        lastmacro = ""
        noplurial = []

# No need to show the plurial forms.
        for onemacro in macros:
            if noplurial \
            and onemacro.startswith(noplurial[-1]):
                continue

            noplurial.append(onemacro)

        for i, word in enumerate(noplurial[::2]):
            nextword = noplurial[2*i+1]

            exafilename = f"{word}-{nextword}"
            texcodes = [
                f"\\{word}{{donnée 1}}",
                f"\\{nextword}{{donnée 2}}"
            ]

            latexcodes[kind].append((exafilename, texcodes))

# Other kind of keywords use the same behavior contrary to the input ones.
        continue


    elif kind == "block":
        nbexa    = 0
        texcodes = []

        for onemacro in macros:
            nbexa += 1

            texcodes += [
                "",
                f"% Possibilité {nbexa}",
                f"\\{onemacro}{{Instruction {nbexa}}}"
            ]

        exafilename = f"main-{kind}"
        texcodes = texcodes[1:]


    elif kind in ["for", "repeat"]:
        nbexa     = 0

        for onemacro in macros:
            nbexa   += 1
            texcodes = []

            if kind == "repeat":
                nbexa = ""

            texcodes += [
                f"\\{onemacro}{{$i \\in uneliste$}}{{",
                " "*2 + f"Instruction {nbexa}",
                "}"
            ]

            exafilename = f"{onemacro}-loop"

            latexcodes[kind].append((exafilename, texcodes))

# Other kind of keywords use the same behavior contrary to the input ones.
        continue


    elif kind == "switch":
        texcodes = ["\\Switch{$i$}{"]

        prefix = "u"

        for i in range(1, 4):
            if i == 3:
                prefix = ""

            texcodes.append(
                " "*2 + f"\\{prefix}Case{{$i = {i-1}$}}{{Instruction {i}}}"
            )

        texcodes.append("}")

        exafilename = kind


    elif kind == "ifelif":
        exafilename = kind

        texcodes = [
            "\\uIf{$i = 0$}{",
            "  Instruction 1",
            "}",
            "\\uElseIf{$i = 1$}{",
            "  Instruction 2",
            "}",
            "\\Else{",
            "  Instruction 3",
            "}"
        ]

    else:
        prefix   = ""

        texcodes = []

        while macros:
            word      = macros.pop(0)
            wordlower = word.lower()

            if wordlower == "and":
                wordbis = macros.pop(0)
                texcodes.append(f"{prefix}A \\{word} B \\{wordbis} C")

            elif wordlower in ["ask", "print"]:
                texcodes.append(f"{prefix}\\{word} \"Quelque chose\"")

            elif wordlower == "return":
                texcodes.append(f"{prefix}\\{word} RÉSULTAT")

            elif wordlower.endswith("from"):
                wordbis = macros.pop(0)
                texcodes.append(f"{prefix}$k$ \\{word} $1$ \\{wordbis} $n$")

            elif wordlower == "inthis":
                texcodes.append(f"{prefix}$e$ \\{word}" + " $\{ 1 , 4 , 16 \}$")

            else:
                texcodes.append(f"{prefix}$L$ \\{word}")

            if not prefix:
                prefix = r"\\ "

        exafilename = kind

# We can store...
    latexcodes[kind].append((exafilename, texcodes))

for kind in latexcodes:
    print()
    print(kind)
    for l in latexcodes[kind]:
        print(l)

# Just normalisze all.
for kind, metas in latexcodes.items():
    for i, (exafilename, onetexcode) in enumerate(metas):
        exafilename = exafilename.lower()
        onetexcode  = LATEX_N_OUPUT_TEMP.format(
            latexcode = " "*2 + "\n  ".join(onetexcode)
        )

        metas[i] = (exafilename, onetexcode)

    latexcodes[kind] = metas


# ------------------------------ #
# -- USEFUL TEXT MACROS - DOC -- #
# ------------------------------ #

text_start, _, text_end = between(
    text = template_tex,
    seps = [
        "% == Text tools - START == %\n",
        "\n% == Text tools - END == %"
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

texcode = "\n".join(texcode + [""])

template_tex = text_start + texcode + text_end


# ------------------------ #
# -- THE EXAMPLES - DOC -- #
# ------------------------ #

text_start, _, text_end = between(
    text = template_tex,
    seps = [
        "% == Block and words tools - START == %\n",
        "\n% == Block and words tools - END == %"
    ],
    keepseps = True
)

texdoc = []


for kind, metas in latexcodes.items():
    explanations = "\n".join(docinfos[kind])

    texdoc.append(
f"""
\\subsubsection{{{peuftitles[kind]}}}

{explanations}

"""
    )

    for (exafilename, onetexcode) in metas:
        texdoc.append(
f"\\codeasideoutput{{examples/algo-basic/additional-macros/{exafilename}.tex}}"
        )

        pathfile = THIS_EXA_DIR / f"{exafilename}.tex"
        pathfile.create(
            kind = 'file',
        )

        with open(
            file     = pathfile,
            mode     = 'w',
            encoding = 'utf-8'
        ) as texfile:
            texfile.write(onetexcode)

texdoc = "\n".join(texdoc + [""])

template_tex = text_start + texdoc + text_end


# ----------------------------- #
# -- UPDATING THE LATEX FILE -- #
# ----------------------------- #

with open(
    file     = TEX_FILE,
    mode     = 'w',
    encoding = 'utf-8'
) as docfile:
    docfile.write(template_tex)
