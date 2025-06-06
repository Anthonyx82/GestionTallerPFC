import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'Taller API'
copyright = '2025, Antonio Martin Sosa'
author = 'Antonio Martin Sosa'
release = '2.0.0'

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinxcontrib.httpdomain"
]

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'preamble': r'''
\usepackage[utf8]{inputenc}
\usepackage{underscore}

% Fuente Arial para texto general
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

% Cargar tabulary normalmente
\usepackage{tabulary}

% Colores naranja para enlaces, títulos y código
\usepackage{xcolor}
\definecolor{sphinxorange}{RGB}{255,140,0}
\definecolor{sphinxorangeLink}{RGB}{255,165,79}
\definecolor{sphinxorangeCode}{RGB}{255,120,0}

% Configuración hipervínculos
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=sphinxorange,
    urlcolor=sphinxorangeLink,
    citecolor=sphinxorange,
    filecolor=sphinxorange,
}

% Color naranja para todos los títulos (niveles)
\usepackage{sectsty}
\allsectionsfont{\color{sphinxorange}}

% Título nivel 2: tamaño 15 pt, negrita, naranja
\usepackage{titlesec}
\titleformat{\section}
  {\normalfont\bfseries\fontsize{15}{18}\selectfont\color{sphinxorange}}
  {\thesection}{1em}{}

% Título nivel 3: tamaño 11 pt, negrita, naranja
\titleformat{\subsection}
  {\normalfont\bfseries\fontsize{11}{14}\selectfont\color{sphinxorange}}
  {\thesubsection}{1em}{}

% Código inline en Roboto Mono negrita 11pt naranja
\usepackage{inconsolata} % fuente monospace buena y compatible con pdflatex
\newcommand{\robotoMonoBold}{\fontseries{b}\selectfont\ttfamily}
\renewcommand{\sphinxcode}[1]{\textcolor{sphinxorangeCode}{{\robotoMonoBold #1}}}

% Código en negrita dentro de bloques (sin cambiar)
\renewcommand{\sphinxbfcode}[1]{\textbf{\sphinxcode{#1}}}

% Código con comillas invertidas
\renewcommand{\sphinxupquote}[1]{\texttt{#1}}

% Estilo para encabezados de tablas (normal + negrita)
\renewcommand{\sphinxstyletheadfamily}{\normalfont\bfseries}
''',
}

templates_path = ['_templates']
exclude_patterns = []

language = 'es'

html_theme = 'furo'
html_static_path = ['_static']
html_logo = "_static/logo.webp"
html_title = "Taller API - Documentación"
