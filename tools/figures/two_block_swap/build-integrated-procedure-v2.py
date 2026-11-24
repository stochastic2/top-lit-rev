"""Build the integrated Markdown note as LaTeX, plus vector circuit assets.

python3 -B notes/build-integrated-procedure-v2.py
python3 -B notes/build-integrated-procedure-v2.py --render

The render option requires pdflatex, pdftoppm, Pillow, and pdfplumber.
The existing atlas source is read without executing its generator.
"""
from pathlib import Path
import re
import sys
import subprocess
import shutil

ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / 'notes'
PROJECT = NOTES / 'integrated-procedure-v2-latex'
FIGS = NOTES / 'figures/c4-helix/integrated-v2'
MD = NOTES / 'full_procedure_integrated_v2.md'
BUILD = ROOT / 'tmp/pdfs/integrated-procedure-v2'
atlas = (NOTES / 'full-circuit-latex/main.tex').read_text()
pages = [re.findall(r'\\begin\{quantikz\}.*?\\end\{quantikz\}', p, re.S)
         for p in atlas.split(r'\newpage')]
assert [len(p) for p in pages] == [2, 3, 2, 2, 1, 5, 2, 2, 4, 3, 1, 2, 0]


def circuit(code):
    return ('\\begin{center}\\begin{adjustbox}{max width=\\linewidth}\n'
            + code + '\n\\end{adjustbox}\\end{center}\n')


def pair(a, b, left, right):
    return (r'\par\noindent\begin{minipage}[t]{.485\linewidth}\centering\small\textbf{'
            + left + '}\n' + circuit(a)
            + r'\end{minipage}\hfill\begin{minipage}[t]{.485\linewidth}\centering\small\textbf{'
            + right + '}\n' + circuit(b) + r'\end{minipage}\par' + '\n')


snips = {
    'cat-preparation': circuit(pages[0][0]),
    'cat-verification': circuit(pages[0][1]),
    'pauli-checks': pair(*pages[1][1:3], 'XXXX check', 'ZZZZ check'),
    'graph-preparation': circuit(pages[2][0]),
    'resource-edge-check': circuit(pages[2][1]),
    'resource-star-check': pair(*pages[3], 'Leaves 0--4', 'Leaves 5--8'),
    'enrichment': circuit(pages[4][0]),
    'vertex-frame': (pair(*pages[5][:2], r'$b_b$ selects $Z_{A_7}$', r'$b_c$ selects $Z_{A_{11}}$')
                     + r'\vspace{3mm}' + '\n'
                     + pair(*pages[5][2:4], r'$b_d$ selects $Z_{A_3}$', r'$b_e$ selects $Z_{A_0}$')),
    'paired-check': pair(*pages[6], 'B ports: leaves 0--3', 'C ports: leaves 4--7'),
    'cycle-checks': pair(*pages[7], 'Parallel edges 7,15', 'Triangle 7,8,11'),
    'gauss-check': (pair(*pages[8][:2], 'Gauge ports 0--3', 'Gauge ports 4--7')
                    + r'\vspace{3mm}' + '\n'
                    + pair(*pages[8][2:], 'Data-pair ports 8--9', 'Data-pair ports 10--11')),
    'gauge-readout-decode': circuit(pages[9][0]) + circuit(pages[9][1]),
    'ungauge-swaps': circuit(pages[9][2]),
    'recovery-correction': circuit(pages[10][0]),
    'logical-readout': circuit(pages[11][0]) + circuit(pages[11][1]),
}

PREAMBLE = r'''\documentclass[11pt]{article}
\usepackage[a4paper,margin=18mm,headheight=14pt,footskip=10mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,microtype,amsmath,amssymb,adjustbox,xcolor,graphicx}
\usepackage{quantikz}
\usepackage{fancyhdr,hyperref,caption,needspace}
\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,
pdftitle={C4-Helix magic preparation: circuit, state, and fault tolerance (V2)}}
\definecolor{ink}{HTML}{203044}
\definecolor{cat}{HTML}{986F14}
\definecolor{gauge}{HTML}{148E9E}
\definecolor{groupa}{HTML}{367AAF}
\definecolor{groupb}{HTML}{D47D28}
\definecolor{groupc}{HTML}{378957}
\definecolor{groupd}{HTML}{8863AF}
\definecolor{groupe}{HTML}{CA5D85}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setlength{\emergencystretch}{2em}
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\captionsetup{font=small,labelfont=bf,hypcap=false}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\color{ink}C4-Helix / procedure and proof}
\fancyhead[R]{\small Expanded V2 / single cycle}
\fancyfoot[R]{\thepage}
\renewcommand{\headrulewidth}{.3pt}
\begin{document}
'''

ESCAPES = {'&': r'\&', '%': r'\%', '#': r'\#', '_': r'\_', '$': r'\$',
           '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
           '^': r'\textasciicircum{}', '\\': r'\textbackslash{}'}


def escape(text):
    return ''.join(ESCAPES.get(c, c) for c in text)


def inline(text):
    """Protect math/link/bold spans, escape only the surrounding prose."""
    rx = re.compile(r'\\\(.*?\\\)|\*\*.*?\*\*|\[[^\]]+\]\([^)]+\)', re.S)
    out, pos = [], 0
    for m in rx.finditer(text):
        out.append(escape(text[pos:m.start()]))
        token = m.group()
        if token.startswith(r'\('):
            out.append(token)
        elif token.startswith('**'):
            out.append(r'\textbf{' + inline(token[2:-2]) + '}')
        else:
            hit = re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)', token)
            label, url = hit.groups()
            if url.startswith(('http://', 'https://')):
                out.append(r'\href{' + url + '}{' + inline(label) + '}')
            else:
                out.append(inline(label))
        pos = m.end()
    out.append(escape(text[pos:]))
    return ''.join(out)


def convert(markdown):
    lines = markdown.splitlines()
    result, paragraph = [], []
    in_list = False
    appendix = False

    def flush():
        if paragraph:
            result.append(inline(' '.join(paragraph)) + '\n\n')
            paragraph.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            result.append('\\end{itemize}\n\n')
            in_list = False

    i = 0
    while i < len(lines):
        line = lines[i]
        if line == r'\[':
            flush()
            close_list()
            math = []
            i += 1
            while i < len(lines) and lines[i] != r'\]':
                math.append(lines[i])
                i += 1
            assert i < len(lines), 'Unclosed display math'
            result.append('\\[\n' + '\n'.join(math) + '\n\\]\n\n')
        elif line.startswith('# '):
            flush()
            close_list()
            title_parts = line[2:].split(': ', 1)
            result.append(r'{\LARGE\bfseries\color{ink}' + inline(title_parts[0]) + r'\par}' + '\n')
            if len(title_parts) == 2:
                result.append(r'\vspace{2mm}{\large\bfseries\color{ink}' + inline(title_parts[1]) + r'\par}' + '\n')
            result.append('\\vspace{3mm}\n')
        elif line.startswith('## '):
            flush()
            close_list()
            title = line[3:]
            if title.startswith('Appendix '):
                if not appendix:
                    result.append('\\clearpage\\appendix\n')
                    appendix = True
                title = re.sub(r'^Appendix [A-Z]\. ', '', title)
            else:
                title = re.sub(r'^\d+\. ', '', title)
            result.append(r'\Needspace{8\baselineskip}\section{' + inline(title) + '}\n')
        elif line.startswith('### '):
            flush()
            close_list()
            title = re.sub(r'^\d+\.\d+\. ', '', line[4:])
            result.append(r'\Needspace{6\baselineskip}\subsection{' + inline(title) + '}\n')
        elif line.startswith('!['):
            flush()
            close_list()
            m = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            assert m, line
            caption, url = m.groups()
            slug = Path(url).stem
            if slug in snips:
                code = r'\input{circuits/' + slug + '.tex}'
            else:
                image_dir = PROJECT / 'images'
                image_dir.mkdir(exist_ok=True)
                image_file = image_dir / Path(url).name
                shutil.copyfile((NOTES / url).resolve(), image_file)
                code = r'\includegraphics[width=\linewidth]{images/' + image_file.name + '}'
            result.append(r'\begin{center}\begin{minipage}{\linewidth}' + '\n'
                          + code + '\n' + r'\captionof{figure}{' + inline(caption) + '}'
                          + '\n' + r'\end{minipage}\end{center}' + '\n\n')
        elif line.startswith('- '):
            flush()
            if not in_list:
                result.append('\\begin{itemize}\\setlength\\itemsep{1pt}\n')
                in_list = True
            result.append('\\item ' + inline(line[2:]) + '\n')
        elif in_list and line.startswith('  ') and line.strip():
            result.append(inline(line.strip()) + '\n')
        elif not line.strip():
            flush()
            close_list()
        else:
            close_list()
            paragraph.append(line)
        i += 1
    flush()
    close_list()
    return ''.join(result)


PROJECT.mkdir(parents=True, exist_ok=True)
(PROJECT / 'circuits').mkdir(exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)
for name, code in snips.items():
    (PROJECT / 'circuits' / f'{name}.tex').write_text(code)
(PROJECT / 'main.tex').write_text(PREAMBLE + convert(MD.read_text()) + '\n\\end{document}\n')

preview_preamble = PREAMBLE.split(r'\begin{document}')[0]
preview_preamble = preview_preamble.replace(r'\pagestyle{fancy}', r'\pagestyle{empty}')
preview_preamble += r'\usepackage[active,tightpage]{preview}' + '\n'
preview_preamble += r'\setlength\PreviewBorder{6pt}' + '\n' + r'\begin{document}' + '\n'
preview_body = []
for name in snips:
    preview_body.append(r'\begin{preview}\begin{minipage}{17cm}\centering' + '\n'
                        + r'\input{circuits/' + name + '.tex}' + '\n'
                        + r'\end{minipage}\end{preview}' + '\n')
(PROJECT / 'circuit-previews.tex').write_text(preview_preamble + ''.join(preview_body) + r'\end{document}')
(FIGS / 'page-order.txt').write_text('\n'.join(snips) + '\n')
print('Generated integrated LaTeX and', len(snips), 'vector circuit snippets', flush=True)

if '--render' in sys.argv:
    from PIL import Image
    import pdfplumber
    BUILD.mkdir(parents=True, exist_ok=True)

    def compile_tex(name):
        with (BUILD / f'{name}.stdout').open('w') as log:
            subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                            f'-output-directory={BUILD}', name + '.tex'],
                           cwd=PROJECT, stdout=log, stderr=subprocess.STDOUT, check=True)

    compile_tex('main')
    compile_tex('main')
    compile_tex('circuit-previews')
    output = ROOT / 'output/pdf/full_procedure_integrated_v2.pdf'
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(BUILD / 'main.pdf', output)
    subprocess.run(['pdftoppm', '-r', '180', '-png', str(BUILD / 'circuit-previews.pdf'),
                    str(BUILD / 'circuit')], check=True)
    with pdfplumber.open(BUILD / 'circuit-previews.pdf') as pdf:
        assert len(pdf.pages) == len(snips), len(pdf.pages)
    for i, name in enumerate(snips, 1):
        with Image.open(BUILD / f'circuit-{i:02}.png') as im:
            im.convert('RGB').save(FIGS / f'{name}.png')
    with pdfplumber.open(output) as pdf:
        print('Compiled integrated PDF:', len(pdf.pages), 'pages', flush=True)
    print('Exported', len(snips), 'circuit images and', output, flush=True)
